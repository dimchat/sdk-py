# -*- coding: utf-8 -*-
#
#   DIM-SDK : Decentralized Instant Messaging Software Development Kit
#
#                                Written in 2019 by Moky <albert.moky@gmail.com>
#
# ==============================================================================
# MIT License
#
# Copyright (c) 2019 Albert Moky
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==============================================================================

"""
    Facebook
    ~~~~~~~~

    Barrack for cache entities
"""

from abc import abstractmethod
from typing import Optional

from dimp import NetworkID, ID, Address
from dimp import User, Group
from dimp import Meta, Profile
from dimp import Barrack

from .network import ServiceProvider, Station, Robot
from .group import Polylogue


class Facebook(Barrack):

    #
    #   Meta
    #
    @staticmethod
    def verify_meta(meta: Meta, identifier: ID) -> bool:
        assert meta is not None, 'meta should not be empty'
        return meta.match_identifier(identifier)

    @abstractmethod
    def save_meta(self, meta: Meta, identifier: ID) -> bool:
        """ Save meta into local storage """
        raise NotImplemented

    #
    #   Profile
    #
    def verify_profile(self, profile: Profile, identifier: ID=None) -> bool:
        assert profile is not None, 'profile should not be empty'
        if identifier is None:
            identifier = self.identifier(profile.identifier)
            assert identifier is not None, 'profile error: %s ' % profile
        elif identifier != profile.identifier:
            # profile ID not match
            return False
        # NOTICE: if this is a group profile,
        #             verify it with each member's meta.key
        #         else (this is a user profile)
        #             verify it with the user's meta.key
        if identifier.is_group:
            # check by each member
            members = self.members(identifier=identifier)
            if members is not None:
                for item in members:
                    meta = self.meta(identifier=item)
                    if meta is None:
                        # FIXME: meta not found for this member
                        continue
                    if profile.verify(public_key=meta.key):
                        return True
            # DISCUSS: what to do about assistants?

            # check by owner
            owner = self.owner(identifier=identifier)
            if owner is None:
                if identifier.type == NetworkID.Polylogue:
                    # NOTICE: if this is a polylogue profile
                    #             verify it with the founder's meta.key
                    #             (which equals to the group's meta.key)
                    meta = self.meta(identifier=identifier)
                else:
                    # FIXME: owner not found for this group
                    return False
            elif owner in members:
                # already checked
                return False
            else:
                meta = self.meta(identifier=owner)
        else:
            assert identifier.is_user, 'profile ID error: %s' % identifier
            meta = self.meta(identifier=identifier)
        if meta is not None:
            return profile.verify(public_key=meta.key)

    @abstractmethod
    def save_profile(self, profile: Profile, identifier: ID=None) -> bool:
        """ Save profile into database """
        raise NotImplemented

    #
    #   Group Members
    #
    @abstractmethod
    def save_members(self, members: list, identifier: ID) -> bool:
        """ Save members into database """
        raise NotImplemented

    #
    #   All local users (for decrypting received message)
    #
    @property
    def local_users(self) -> Optional[list]:
        raise NotImplemented

    #
    #   Current user (for signing and sending message)
    #
    @property
    def current_user(self) -> Optional[User]:
        users = self.local_users
        if users is not None and len(users) > 0:
            return users[0]

    def __identifier(self, address: Address) -> Optional[ID]:
        """ generate ID from meta with address """
        identifier = ID.new(address=address)
        meta = self.meta(identifier=identifier)
        if meta is None:
            # failed to get meta for this address
            return None
        seed = meta.seed
        if seed is None or len(seed) == 0:
            return identifier
        identifier = meta.generate_identifier(address.network)
        self.cache_id(identifier)
        return identifier

    def create_identifier(self, string: str) -> ID:
        if isinstance(string, Address):
            # convert Address to ID
            return self.__identifier(address=string)
        assert isinstance(string, str), 'ID error: %s' % string
        return ID(string)

    def create_user(self, identifier: ID) -> User:
        assert identifier.is_user, 'user ID error: %s' % identifier
        if identifier.is_broadcast:
            # create user 'anyone@anywhere'
            return User(identifier=identifier)
        # make sure meta exists
        assert self.meta(identifier) is not None, 'failed to get meta for user: %s' % identifier
        # check user type
        u_type = identifier.type
        if u_type == NetworkID.Main or u_type == NetworkID.BTCMain:
            return User(identifier=identifier)
        if u_type == NetworkID.Robot:
            return Robot(identifier=identifier)
        if u_type == NetworkID.Station:
            return Station(identifier=identifier)
        raise TypeError('unsupported user type: %s' % u_type)

    def create_group(self, identifier: ID) -> Group:
        assert identifier.is_group, 'group ID error: %s' % identifier
        if identifier.is_broadcast:
            # create group 'everyone@everywhere'
            return Group(identifier=identifier)
        # make sure meta exists
        assert self.meta(identifier) is not None, 'failed to get meta for group: %s' % identifier
        # check group type
        g_type = identifier.type
        if g_type == NetworkID.Polylogue:
            return Polylogue(identifier=identifier)
        if g_type == NetworkID.Chatroom:
            raise NotImplementedError('Chatroom not implemented')
        if g_type == NetworkID.Provider:
            return ServiceProvider(identifier=identifier)
        raise TypeError('unsupported group type: %s' % g_type)

    #
    #   GroupDataSource
    #
    def founder(self, identifier: ID) -> Optional[ID]:
        uid = super().founder(identifier=identifier)
        if uid is not None:
            return uid
        # check each member's public key with group meta
        members = self.members(identifier=identifier)
        if members is not None:
            meta = self.meta(identifier=identifier)
            if meta is not None:
                # if the member's public key matches with the group's meta,
                # it means this meta was generate by the member's private key
                for item in members:
                    m = self.meta(identifier=self.identifier(item))
                    if m is not None and meta.match_public_key(m.key):
                        # got it
                        return item
        # TODO: load founder from database

    def owner(self, identifier: ID) -> ID:
        uid = super().owner(identifier=identifier)
        if uid is not None:
            return uid
        # check group type
        if identifier.type == NetworkID.Polylogue:
            # Polylogue's owner is its founder
            return self.founder(identifier=identifier)
        # TODO: load owner from database

    def is_founder(self, member: ID, group: ID) -> bool:
        # check member's public key with group's meta.key
        g_meta = self.meta(identifier=group)
        if g_meta is None:
            raise LookupError('failed to get meta for group: %s' % group)
        m_meta = self.meta(identifier=member)
        if m_meta is None:
            raise LookupError('failed to get meta for member: %s' % member)
        return g_meta.match_public_key(m_meta.key)

    def is_owner(self, member: ID, group: ID) -> bool:
        if group.type == NetworkID.Polylogue:
            return self.is_founder(member=member, group=group)
        else:
            raise NotImplementedError('only Polylogue so far')

    def exists_member(self, member: ID, group: ID) -> bool:
        members = self.members(identifier=group)
        if members is not None and member in members:
            return True
        owner = self.owner(identifier=group)
        if member == owner:
            return True

    #
    #   Group Assistants
    #
    @abstractmethod
    def assistants(self, identifier: ID) -> Optional[list]:
        """ Get assistants for this group """
        raise NotImplemented

    def exists_assistant(self, member: ID, group: ID) -> bool:
        assistants = self.assistants(identifier=group)
        if assistants is not None:
            return member in assistants
