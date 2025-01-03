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
from .mkm import User, UserDataSource
from .mkm import Group, GroupDataSource

from .archivist import Archivist


class Facebook(Barrack, UserDataSource, GroupDataSource, ABC):

    @property
    @abstractmethod
    def archivist(self) -> Archivist:
        raise NotImplemented

    # Override
    def cache_user(self, user: User):
        if user.data_source is None:
            user.data_source = self
        super().cache_user(user=user)

    # Override
    def cache_group(self, group: Group):
        if group.data_source is None:
            group.data_source = self
        super().cache_group(group=group)

    #
    #   Entity Delegate
    #

    # Override
    async def get_user(self, identifier: ID) -> Optional[User]:
        assert identifier.is_user, 'user ID error: %s' % identifier
        # 1. get from user cache
        user = await super().get_user(identifier=identifier)
        if user is None:
            # 2. create user and cache it
            user = await self.archivist.create_user(identifier=identifier)
            if user is not None:
                self.cache_user(user=user)
        return user

    # Override
    async def get_group(self, identifier: ID) -> Optional[Group]:
        assert identifier.is_group, 'group ID error: %s' % identifier
        # 1. get from group cache
        group = await super().get_group(identifier=identifier)
        if group is None:
            # 2. create group and cache it
            group = await self.archivist.create_group(identifier=identifier)
            if group is not None:
                self.cache_group(group=group)
        return group

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
        users = await self.archivist.local_users
        if users is None or len(users) == 0:
            # assert False, 'local users should not be empty'
            return None
        elif receiver.is_broadcast:
            # broadcast message can decrypt by anyone, so just return current user
            return users[0]
        # 1. personal message
        # 2. split group message
        for item in users:
            if item.identifier == receiver:
                # DISCUSS: set this item to be current user?
                return item
        # not me?
        return None

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
    #   User DataSource
    #

    # Override
    async def public_key_for_encryption(self, identifier: ID) -> Optional[EncryptKey]:
        assert identifier.is_user, 'user ID error: %s' % identifier
        db = self.archivist
        # 1. get key from visa
        key = await db.get_visa_key(identifier=identifier)
        if key is not None:
            # if visa.key exists, use it for encryption
            return key
        # 2. get key from meta
        key = await db.get_meta_key(identifier=identifier)
        if isinstance(key, EncryptKey):
            # if visa.key not exists and meta.key is encrypt key,
            # use it for encryption
            return key

    # Override
    async def public_keys_for_verification(self, identifier: ID) -> List[VerifyKey]:
        # assert identifier.is_user, 'user ID error: %s' % identifier
        keys: List[VerifyKey] = []
        db = self.archivist
        # 1. get key from visa
        key = await db.get_visa_key(identifier=identifier)
        if isinstance(key, VerifyKey):
            # the sender may use communication key to sign message.data,
            # so try to verify it with visa.key first
            keys.append(key)
        # 2. get key from meta
        key = await db.get_meta_key(identifier=identifier)
        if key is not None:
            # the sender may use identity key to sign message.data,
            # try to verify it with meta.key too
            keys.append(key)
        assert len(keys) > 0, 'failed to get verify key for user: %s' % identifier
        return keys
