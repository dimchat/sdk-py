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

import time
import weakref
from abc import abstractmethod
from typing import Optional

from dimp import PrivateKey, SignKey, DecryptKey
from dimp import NetworkID, ID, Address
from dimp import User, Group
from dimp import Meta, Profile
from dimp import Barrack

from .ans import AddressNameService
from .network import ServiceProvider, Station, Robot
from .group import Polylogue


class Facebook(Barrack):

    EXPIRES = 3600  # profile expires (1 hour)

    def __init__(self):
        super().__init__()
        self.__ans: weakref.ReferenceType = None
        # caches
        self.__profiles: dict = {}
        self.__private_keys: dict = {}
        self.__contacts: dict = {}
        self.__members: dict = {}

    @property
    def ans(self) -> AddressNameService:
        if self.__ans is not None:
            return self.__ans()

    @ans.setter
    def ans(self, value: AddressNameService):
        self.__ans = weakref.ref(value)

    def ans_get(self, name: str) -> ID:
        ans = self.ans
        if ans is not None:
            return ans.identifier(name=name)

    #
    #   Meta
    #
    @staticmethod
    def verify_meta(meta: Meta, identifier: ID) -> bool:
        assert meta is not None, 'meta should not be empty'
        return meta.match_identifier(identifier)

    def cache_meta(self, meta: Meta, identifier: ID) -> bool:
        if not self.verify_meta(meta=meta, identifier=identifier):
            return False
        return super().cache_meta(meta=meta, identifier=identifier)

    @abstractmethod
    def save_meta(self, meta: Meta, identifier: ID) -> bool:
        """ Save meta into local storage """
        raise NotImplemented

    @abstractmethod
    def load_meta(self, identifier: ID) -> Optional[Meta]:
        """ Load meta from local storage """
        raise NotImplemented

    #
    #   Profile
    #
    def verify_profile(self, profile: Profile, identifier: ID=None) -> bool:
        assert profile is not None, 'profile should not be empty'
        if identifier is not None and profile.identifier != identifier:
            # profile ID not match
            return False
        if identifier is None:
            identifier = self.identifier(profile.identifier)
            assert identifier is not None, 'profile error: %s ' % profile
        # NOTICE: if this is a group profile,
        #             verify it with each member's meta.key
        #         else (this is a user profile)
        #             verify it with the user's meta.key
        if identifier.type.is_group():
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
            assert identifier.type.is_user(), 'profile ID error: %s' % identifier
            meta = self.meta(identifier=identifier)
        if meta is not None:
            return profile.verify(public_key=meta.key)

    def cache_profile(self, profile: Profile, identifier: ID=None) -> bool:
        if profile is None:
            # remove from cache if exists
            self.__profiles.pop(identifier, None)
            return False
        if not self.verify_profile(profile=profile, identifier=identifier):
            return False
        if identifier is None:
            identifier = self.identifier(string=profile.identifier)
        self.__profiles[identifier] = profile
        return True

    @abstractmethod
    def save_profile(self, profile: Profile, identifier: ID=None) -> bool:
        """ Save profile into database """
        raise NotImplemented

    @abstractmethod
    def load_profile(self, identifier: ID) -> Optional[Profile]:
        """ Load profile from database """
        raise NotImplemented

    #
    #   Private keys
    #
    def verify_private_key(self, key: PrivateKey, identifier: ID) -> bool:
        assert key is not None, 'private key should not be empty'
        meta = self.meta(identifier=identifier)
        assert meta is not None, 'meta not found: %s' % identifier
        assert meta.key is not None, 'meta error: %s, %s' % (identifier, meta)
        return meta.key.match(private_key=key)

    def cache_private_key(self, key: PrivateKey, identifier: ID) -> bool:
        assert identifier.type.is_user(), 'user ID error: %s' % identifier
        if key is None:
            self.__private_keys.pop(identifier, None)
            return False
        if not self.verify_private_key(key=key, identifier=identifier):
            return False
        self.__private_keys[identifier] = key
        return True

    @abstractmethod
    def save_private_key(self, key: PrivateKey, identifier: ID) -> bool:
        """ Save private key into safety storage """
        raise NotImplemented

    @abstractmethod
    def load_private_key(self, identifier: ID) -> Optional[PrivateKey]:
        """ Load private key from safety storage """
        raise NotImplemented

    #
    #   User Contacts
    #
    def cache_contacts(self, contacts: list, identifier: ID) -> bool:
        assert identifier.type.is_user(), 'user ID error: %s' % identifier
        if contacts is None:
            self.__contacts.pop(identifier, None)
            return False
        self.__contacts[identifier] = contacts
        return True

    @abstractmethod
    def save_contacts(self, contacts: list, identifier: ID) -> bool:
        """ Save contacts into database """
        raise NotImplemented

    @abstractmethod
    def load_contacts(self, identifier: ID) -> Optional[list]:
        """ Load contacts from database """
        raise NotImplemented

    #
    #   Group Members
    #
    def cache_members(self, members: list, identifier: ID) -> bool:
        assert identifier.type.is_group(), 'group ID error: %s' % identifier
        if members is None:
            self.__members.pop(identifier, None)
            return False
        self.__members[identifier] = members
        return True

    @abstractmethod
    def save_members(self, members: list, identifier: ID) -> bool:
        """ Save members into database """
        raise NotImplemented

    @abstractmethod
    def load_members(self, identifier: ID) -> Optional[list]:
        """ Load members from database """
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
        # try from ANS record
        identifier = self.ans_get(name=string)
        if identifier is not None:
            return identifier
        # create by barrack
        return super().create_identifier(string=string)

    def create_user(self, identifier: ID) -> User:
        assert identifier.type.is_user(), 'user ID error: %s' % identifier
        if identifier.is_broadcast:
            # create user 'anyone@anywhere'
            return User(identifier=identifier)
        # make sure meta exists
        assert self.meta(identifier) is not None, 'failed to get meta for user: %s' % identifier
        # TODO: check user type
        u_type = identifier.type
        if u_type.is_person():
            return User(identifier=identifier)
        if u_type.is_robot():
            return Robot(identifier=identifier)
        if u_type.is_station():
            return Station(identifier=identifier)
        raise TypeError('unsupported user type: %s' % u_type)

    def create_group(self, identifier: ID) -> Group:
        assert identifier.type.is_group(), 'group ID error: %s' % identifier
        if identifier.is_broadcast:
            # create group 'everyone@everywhere'
            return Group(identifier=identifier)
        # make sure meta exists
        assert self.meta(identifier) is not None, 'failed to get meta for group: %s' % identifier
        # TODO: check group type
        g_type = identifier.type
        if g_type == NetworkID.Polylogue:
            return Polylogue(identifier=identifier)
        if g_type == NetworkID.Chatroom:
            raise NotImplementedError('Chatroom not implemented')
        if g_type.is_provider():
            return ServiceProvider(identifier=identifier)
        raise TypeError('unsupported group type: %s' % g_type)

    #
    #   EntityDataSource
    #
    def meta(self, identifier: ID) -> Optional[Meta]:
        info = super().meta(identifier=identifier)
        if info is not None:
            return info
        # load from local storage
        info = self.load_meta(identifier=identifier)
        if info is None:
            return None
        # no need to verify meta from local storage
        super().cache_meta(meta=info, identifier=identifier)
        return info

    EXPIRES_KEY = 'expires'

    def profile(self, identifier: ID) -> Optional[Profile]:
        info = self.__profiles.get(identifier)
        if info is not None:
            # check expired time
            timestamp = time.time() + self.EXPIRES
            expires = info.get(self.EXPIRES_KEY)
            if expires is None:
                # set expired time
                info[self.EXPIRES_KEY] = timestamp
                return info
            elif expires < timestamp:
                # not expired yet
                return info
        # load from local storage
        info = self.load_profile(identifier=identifier)
        if info is None:
            info = Profile.new(identifier=identifier)
        else:
            info.pop(self.EXPIRES_KEY, None)
        # no need to verify profile from local storage
        self.__profiles[identifier] = info
        return info

    #
    #   UserDataSource
    #
    def contacts(self, identifier: ID) -> Optional[list]:
        array = self.__contacts.get(identifier)
        if array is not None:
            return array
        # load from local storage
        array = self.load_contacts(identifier=identifier)
        if array is None:
            return None
        self.cache_contacts(contacts=array, identifier=identifier)
        return array

    def private_key_for_signature(self, identifier: ID) -> Optional[SignKey]:
        key = self.__private_keys.get(identifier)
        if key is not None:
            return key
        # load from local storage
        key = self.load_private_key(identifier=identifier)
        if key is None:
            return None
        self.cache_private_key(key=key, identifier=identifier)
        return key

    def private_keys_for_decryption(self, identifier: ID) -> Optional[list]:
        # DIMP v1.0:
        #     decrypt key not found, use the same with sign key?
        key = self.private_key_for_signature(identifier)
        if isinstance(key, DecryptKey):
            # TODO: support profile.key
            return [key]

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

    def members(self, identifier: ID) -> Optional[list]:
        array = super().members(identifier=identifier)
        if array is None:
            # get from cache
            array = self.__members.get(identifier)
        if array is not None:
            return array
        # load from local storage
        array = self.load_members(identifier=identifier)
        if array is None:
            return None
        self.cache_members(members=array, identifier=identifier)
        return array

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
        if member in members:
            return True
        owner = self.owner(identifier=group)
        if member == owner:
            return True

    #
    #   Group Assistants
    #
    def assistants(self, identifier: ID) -> Optional[list]:
        assert identifier.type.is_group(), 'Group ID error: %s' % identifier
        identifier = self.ans_get(name='assistant')
        if identifier is not None:
            return [identifier]

    def exists_assistant(self, member: ID, group: ID) -> bool:
        assistants = self.assistants(identifier=group)
        if assistants is not None:
            return member in assistants
