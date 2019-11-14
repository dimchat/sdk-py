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

from dimp import NetworkID, ID, Address
from dimp import Meta, Profile, User, Group
from dimp import Barrack, LocalUser, PrivateKey

from .ans import AddressNameService


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
        if value is None:
            self.__ans = None
        else:
            self.__ans = weakref.ref(value)

    #
    #   Meta
    #
    @staticmethod
    def verify_meta(meta: Meta, identifier: ID) -> bool:
        if meta is None:
            return False
        return meta.match_identifier(identifier)

    def cache_meta(self, meta: Meta, identifier: ID) -> bool:
        if not self.verify_meta(meta=meta, identifier=identifier):
            return False
        return super().cache_meta(meta=meta, identifier=identifier)

    @abstractmethod
    def save_meta(self, meta: Meta, identifier: ID) -> bool:
        if super().meta(identifier=identifier) is not None:
            # meta already exists, no need to update again
            return True
        if not self.cache_meta(meta=meta, identifier=identifier):
            return False
        # return True to let subclass save meta into local storage
        return True

    @abstractmethod
    def load_meta(self, identifier: ID) -> Optional[Meta]:
        # return None to let subclass load meta from local storage
        return super().meta(identifier=identifier)

    #
    #   Profile
    #
    def verify_profile(self, profile: Profile, identifier: ID=None) -> bool:
        if profile is None:
            return False
        if identifier is not None and profile.identifier != identifier:
            # profile ID not match
            return False
        if profile.valid:
            # already verified
            return True
        if identifier is None:
            identifier = self.identifier(profile.identifier)
        # try to verify the profile
        if identifier.type.is_user() or identifier.type.value == NetworkID.Polylogue:
            # if this is a user profile,
            #     verify it with the user's meta.key
            # else if this is a polylogue profile,
            #     verify it with the founder's meta.key (which equals to the group's meta.key)
            meta = self.meta(identifier=identifier)
            if meta is not None:
                return profile.verify(public_key=meta.key)
        else:
            raise NotImplementedError('unsupported profile ID: %s' % profile)

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
        if not self.cache_profile(profile=profile, identifier=identifier):
            return False
        # return True to let subclass save profile into database
        return True

    @abstractmethod
    def load_profile(self, identifier: ID) -> Optional[Profile]:
        # return None to let subclass load profile from database
        pass

    #
    #   Private keys
    #
    def cache_private_key(self, key: PrivateKey, identifier: ID) -> bool:
        assert identifier.type.is_user(), 'user ID error: %s' % identifier
        if key is None:
            self.__private_keys.pop(identifier, None)
            return False
        self.__private_keys[identifier] = key
        return True

    @abstractmethod
    def save_private_key(self, key: PrivateKey, identifier: ID) -> bool:
        if not self.cache_private_key(key=key, identifier=identifier):
            return False
        # return True to let subclass save private key into secret storage
        return True

    @abstractmethod
    def load_private_key(self, identifier: ID) -> Optional[PrivateKey]:
        # return None to let subclass load private key from secret storage
        pass

    #
    #   Contacts
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
        if not self.cache_contacts(contacts=contacts, identifier=identifier):
            return False
        # return True to let subclass save contacts into database
        return True

    @abstractmethod
    def load_contacts(self, identifier: ID) -> Optional[list]:
        # return None to let subclass load contacts from database
        pass

    #
    #   Members
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
        if not self.cache_members(members=members, identifier=identifier):
            return False
        # return True to let subclass save members into database
        return True

    @abstractmethod
    def load_members(self, identifier: ID) -> Optional[list]:
        # return None to let subclass load members from database
        pass

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
        identifier = ID.new(name=seed, address=address)
        self.cache_id(identifier)
        return identifier

    #
    #   SocialNetworkDataSource
    #
    def identifier(self, string: str) -> Optional[ID]:
        if string is None:
            return None
        if isinstance(string, Address):
            # get ID with address
            return self.__identifier(address=string)
        if isinstance(string, ID):
            # return ID object directly
            return string
        # check ANS
        if self.ans is not None:
            # try from ANS record
            identifier = self.ans.identifier(name=string)
            if identifier is not None:
                return identifier
        # get from barrack
        return super().identifier(string=string)

    def user(self, identifier: ID) -> Optional[User]:
        #  get from barrack cache
        user = super().user(identifier=identifier)
        if user is not None:
            return user
        # check meta and private key
        meta = self.meta(identifier=identifier)
        if meta is None:
            raise LookupError('meta not found: %s' % identifier)
        if identifier.type.is_person():
            private_key = self.private_key_for_signature(identifier=identifier)
            if private_key is None:
                user = User(identifier=identifier)
            else:
                user = LocalUser(identifier=identifier)
        else:
            raise NotImplementedError('unsupported user type: %s' % identifier)
        # cache it in barrack
        self.cache_user(user=user)
        return user

    def group(self, identifier: ID) -> Optional[Group]:
        # get from barrack cache
        group = super().group(identifier=identifier)
        if group is not None:
            return group
        # check meta
        meta = self.meta(identifier=identifier)
        if meta is None:
            raise LookupError('meta not found: %s' % identifier)
        if identifier.type == NetworkID.Polylogue:
            group = Group(identifier=identifier)
        else:
            raise NotImplementedError('unsupported group type: %s' % identifier)
        # cache it in barrack
        self.cache_group(group=group)
        return group

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
        self.cache_meta(meta=info, identifier=identifier)
        return info

    def profile(self, identifier: ID) -> Optional[Profile]:
        info = super().profile(identifier=identifier)
        if info is None:
            # get from cache
            info = self.__profiles.get(identifier)
        if info is not None:
            # check expired time
            timestamp = time.time() + self.EXPIRES
            expires = info.get('expires')
            if expires is None:
                # set expired time
                info['expires'] = timestamp
                return info
            elif expires < timestamp:
                # not expired yet
                return info
        # load from local storage
        info = self.load_profile(identifier=identifier)
        if info is None:
            return None
        self.cache_profile(profile=info, identifier=identifier)
        return info

    #
    #   UserDataSource
    #
    def private_key_for_signature(self, identifier: ID) -> Optional[PrivateKey]:
        key = super().private_key_for_signature(identifier=identifier)
        if key is None:
            # get from cache
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
        keys = super().private_keys_for_decryption(identifier=identifier)
        if keys is None:
            # DIMP v1.0:
            #     decrypt key not found, use the same with sign key?
            key = self.private_key_for_signature(identifier)
            if key is not None:
                keys = [key]
        return keys

    def contacts(self, identifier: ID) -> Optional[list]:
        array = super().contacts(identifier=identifier)
        if array is None:
            # get from cache
            array = self.__contacts.get(identifier)
        if array is not None:
            return array
        # load from local storage
        array = self.load_contacts(identifier=identifier)
        if array is None:
            return None
        self.cache_contacts(contacts=array, identifier=identifier)
        return array

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

    def owner(self, identifier: ID) -> ID:
        uid = super().owner(identifier=identifier)
        if uid is not None:
            return uid
        if identifier.type == NetworkID.Polylogue:
            # Polylogue's owner is its founder
            return self.founder(identifier=identifier)

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
        if g_meta is not None:
            m_meta = self.meta(identifier=member)
            if m_meta is not None:
                return g_meta.match_public_key(m_meta.key)

    def is_owner(self, member: ID, group: ID) -> bool:
        if group.type == NetworkID.Polylogue:
            return self.is_founder(member=member, group=group)

    def exists_member(self, member: ID, group: ID) -> bool:
        owner = self.owner(identifier=group)
        if owner is not None and owner == member:
            return True
        members = self.members(identifier=group)
        if members is not None:
            return member in members

    #
    #   Group Assistants
    #
    def assistants(self, identifier: ID) -> Optional[list]:
        assert identifier.type.is_group(), 'Group ID error: %s' % identifier
        if self.ans is not None:
            identifier = self.ans.identifier(name='assistant')
            if identifier is not None:
                return [identifier]

    def exists_assistant(self, member: ID, group: ID) -> bool:
        assistants = self.assistants(identifier=group)
        if assistants is not None:
            return member in assistants
