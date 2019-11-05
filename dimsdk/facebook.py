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
from abc import abstractmethod
from typing import Optional

from dimp import NetworkID, ID, Meta, Profile, User, Group
from dimp import Barrack, LocalUser, PrivateKey

from .ans import AddressNameService


class Facebook(Barrack):

    EXPIRES = 3600  # profile expires (1 hour)

    def __init__(self):
        super().__init__()
        self.ans: AddressNameService = None
        # caches
        self.__profiles: dict = {}
        self.__private_keys: dict = {}
        self.__contacts: dict = {}
        self.__members: dict = {}

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
        # TODO: save meta into local storage

    @abstractmethod
    def load_meta(self, identifier: ID) -> Optional[Meta]:
        # TODO: load meta from local storage
        pass

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
        # set expired time
        profile['expires'] = time.time() + self.EXPIRES
        self.__profiles[identifier] = profile
        return True

    @abstractmethod
    def save_profile(self, profile: Profile, identifier: ID=None) -> bool:
        if not self.cache_profile(profile=profile, identifier=identifier):
            return False
        # TODO: save profile into database

    @abstractmethod
    def load_profile(self, identifier: ID) -> Optional[Profile]:
        # TODO: load profile from database
        pass

    #
    #   Private keys
    #
    def cache_private_key(self, key: PrivateKey, identifier: ID) -> bool:
        assert identifier.type.is_user(), 'ID error: %s' % identifier
        if key is None:
            self.__private_keys.pop(identifier, None)
            return False
        self.__private_keys[identifier] = key
        return True

    @abstractmethod
    def save_private_key(self, key: PrivateKey, identifier: ID) -> bool:
        if not self.cache_private_key(key=key, identifier=identifier):
            return False
        # TODO: save private key into secret storage

    @abstractmethod
    def load_private_key(self, identifier: ID) -> Optional[PrivateKey]:
        # TODO: load private key from secret storage
        pass

    #
    #   Contacts
    #
    def cache_contacts(self, contacts: list, identifier: ID) -> bool:
        assert identifier.type.is_user(), 'ID error: %s' % identifier
        if contacts is None:
            self.__contacts.pop(identifier, None)
            return False
        self.__contacts[identifier] = contacts
        return True

    @abstractmethod
    def save_contacts(self, contacts: list, identifier: ID) -> bool:
        if not self.cache_contacts(contacts=contacts, identifier=identifier):
            return False
        # TODO: save contacts into database

    @abstractmethod
    def load_contacts(self, identifier: ID) -> Optional[list]:
        # TODO: load contacts from database
        pass

    #
    #   Members
    #
    def cache_members(self, members: list, identifier: ID) -> bool:
        assert identifier.type.is_group(), 'ID error: %s' % identifier
        if members is None:
            self.__members.pop(identifier, None)
            return False
        self.__members[identifier] = members
        return True

    @abstractmethod
    def save_members(self, members: list, identifier: ID) -> bool:
        if not self.cache_members(members=members, identifier=identifier):
            return False
        # TODO: save members into database

    @abstractmethod
    def load_members(self, identifier: ID) -> Optional[list]:
        # TODO: load members from database
        pass


    #
    #   SocialNetworkDataSource
    #
    def identifier(self, string: str) -> Optional[ID]:
        if string is None:
            return None
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
        if meta is not None:
            # TODO: check user type
            # check private key
            key = self.private_key_for_signature(identifier=identifier)
            if key is None:
                user = User(identifier=identifier)
            else:
                user = LocalUser(identifier=identifier)
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
        if meta is not None:
            # TODO: check group type
            group = Group(identifier=identifier)
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
        if self.cache_meta(meta=info, identifier=identifier):
            return info

    def profile(self, identifier: ID) -> Optional[Profile]:
        info = super().profile(identifier=identifier)
        if info is None:
            # get from cache
            info = self.__profiles.get(identifier)
        if info is not None:
            # check expired time
            expires = info.get('expires')
            if expires < time.time():
                return info
        # load from local storage
        info = self.load_profile(identifier=identifier)
        if self.cache_profile(profile=info, identifier=identifier):
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
        if self.cache_private_key(key=key, identifier=identifier):
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
        if self.cache_contacts(contacts=array, identifier=identifier):
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
        # TODO: load founder from database

    def owner(self, identifier: ID) -> ID:
        uid = super().owner(identifier=identifier)
        if uid is not None:
            return uid
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
        if self.cache_members(members=array, identifier=identifier):
            return array

    def assistants(self, identifier: ID) -> Optional[list]:
        """ Group Assistant Bots """
        assert identifier.type.is_group(), 'group ID error: %s' % identifier
        ass = self.ans.identifier(name='assistant')
        if ass is not None:
            return [ass]
