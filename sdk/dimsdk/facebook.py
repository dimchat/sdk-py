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

from abc import ABC, abstractmethod
from typing import Optional, List

from dimp import EncryptKey, VerifyKey
from dimp import ID, Meta, Document

from .core import Barrack
from .mkm import EntityDelegate, User, Group
from .mkm import UserDataSource, GroupDataSource


class Facebook(EntityDelegate, UserDataSource, GroupDataSource, ABC):

    @property
    @abstractmethod
    def barrack(self) -> Barrack:
        raise NotImplemented

    @abstractmethod
    async def save_meta(self, meta: Meta, identifier: ID) -> bool:
        """
        Save meta for entity ID (must verify first)

        :param meta:       entity meta
        :param identifier: entity ID
        :return: True on success
        """
        raise NotImplemented

    @abstractmethod
    async def save_document(self, document: Document) -> bool:
        """
        Save entity document with ID (must verify first)

        :param document: entity document
        :return: True on success
        """
        raise NotImplemented

    #
    #   Public Keys
    #

    @abstractmethod
    async def get_meta_key(self, identifier: ID) -> Optional[VerifyKey]:
        """
        Get meta.key

        :param identifier: user ID
        :return: None on not found
        """
        raise NotImplemented

    @abstractmethod
    async def get_visa_key(self, identifier: ID) -> Optional[EncryptKey]:
        """
        Get visa.key

        :param identifier: user ID
        :return: None on not found
        """
        raise NotImplemented

    async def select_user(self, receiver: ID) -> Optional[User]:
        """
        Select local user for receiver

        :param receiver: user/group ID
        :return: local user
        """
        if receiver.is_group:
            # group message (recipient not designated)
            # TODO: check members of group
            return None
        else:
            assert receiver.is_user, 'receiver error: %s' % receiver
        users = await self.barrack.local_users
        if users is None or len(users) == 0:
            # assert False, 'local users should not be empty'
            return None
        elif receiver.is_broadcast:
            # broadcast message can decrypt by anyone, so
            # just return current user
            return users[0]
        # 1. personal message
        # 2. split group message
        for item in users:
            if item.identifier == receiver:
                # DISCUSS: set this item to be current user?
                return item
        # not me?
        return None

    #
    #   Entity Delegate
    #

    # Override
    async def get_user(self, identifier: ID) -> Optional[User]:
        assert identifier.is_user, 'user ID error: %s' % identifier
        barrack = self.barrack
        #
        #  1. get from user cache
        #
        user = barrack.get_user(identifier=identifier)
        if user is not None:
            return user
        #
        #  2. check visa key
        #
        if not identifier.is_broadcast:
            visa_key = await self.public_key_for_encryption(identifier=identifier)
            if visa_key is None:
                # assert False, 'visa.key not found: %s' % identifier
                return None
            # NOTICE: if visa.key exists, then visa & meta must exist too.
        #
        #  3. create user and cache it
        #
        user = await barrack.create_user(identifier=identifier)
        if user is not None:
            barrack.cache_user(user=user)
        return user

    # Override
    async def get_group(self, identifier: ID) -> Optional[Group]:
        assert identifier.is_group, 'group ID error: %s' % identifier
        barrack = self.barrack
        #
        #  1. get from group cache
        #
        group = barrack.get_group(identifier=identifier)
        if group is not None:
            return group
        #
        #  2. check members
        #
        if not identifier.is_broadcast:
            members = await self.get_members(identifier=identifier)
            if members is None or len(members) == 0:
                # assert False, 'group members not found: %s' % identifier
                return None
            # NOTICE: if members exist, then owner (founder) must exist,
            #         and bulletin & meta must exist too.
        #
        #  3. create group and cache it
        #
        group = await barrack.create_group(identifier=identifier)
        if group is not None:
            barrack.cache_group(group=group)
        return group

    #
    #   User DataSource
    #

    # Override
    async def public_key_for_encryption(self, identifier: ID) -> Optional[EncryptKey]:
        assert identifier.is_user, 'user ID error: %s' % identifier
        #
        #  1. get key from visa
        #
        visa_key = await self.get_visa_key(identifier=identifier)
        if visa_key is not None:
            # if visa.key exists, use it for encryption
            return visa_key
        #
        #  2. get key from meta
        #
        meta_key = await self.get_meta_key(identifier=identifier)
        if isinstance(meta_key, EncryptKey):
            # if visa.key not exists and meta.key is encrypt key,
            # use it for encryption
            return meta_key

    # Override
    async def public_keys_for_verification(self, identifier: ID) -> List[VerifyKey]:
        # assert identifier.is_user, 'user ID error: %s' % identifier
        keys: List[VerifyKey] = []
        #
        #  1. get key from visa
        #
        visa_key = await self.get_visa_key(identifier=identifier)
        if isinstance(visa_key, VerifyKey):
            # the sender may use communication key to sign message.data,
            # so try to verify it with visa.key first
            keys.append(visa_key)
        #
        #  2. get key from meta
        #
        meta_key = await self.get_meta_key(identifier=identifier)
        if meta_key is not None:
            # the sender may use identity key to sign message.data,
            # try to verify it with meta.key too
            keys.append(meta_key)
        assert len(keys) > 0, 'failed to get verify key for user: %s' % identifier
        return keys
