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

from abc import ABC, abstractmethod
from typing import List, Optional

from dimp import ID

from ..mkm import User, Group


class Barrack(ABC):
    """Entity pool for managing and caching User/Group instances (account entity manager).

    Core responsibilities:
    1. In-memory caching of User/Group entities to avoid repeated creation
    2. Lazy creation of User/Group entities when required metadata is available
    3. Fast lookup of entities by ID (identifier)

    Key design: Acts as a "barracks" (entity pool) to centralize entity management,
    ensuring only one instance exists per ID and reducing redundant data loading.
    """

    @abstractmethod
    def cache_user(self, user: User):
        """
        Caches a User entity in memory (overwrites existing entry for the same ID).

        :param user: user entity
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.cache_user()'
        )

    @abstractmethod
    def cache_group(self, group: Group):
        """
        Caches a Group entity in memory (overwrites existing entry for the same ID).

        :param group: group entity
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.cache_group()'
        )

    @abstractmethod
    def get_user(self, identifier: ID) -> Optional[User]:
        """
        Retrieves a cached User entity by ID.

        :param identifier: user ID
        :return: user entity
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.get_user()'
        )

    @abstractmethod
    def get_group(self, identifier: ID) -> Optional[Group]:
        """
        Retrieves a cached Group entity by ID.

        :param identifier: group ID
        :return: group entity
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.get_group()'
        )

    @abstractmethod
    def create_user(self, identifier: ID) -> Optional[User]:
        """
        Creates a User entity if the required visa key metadata exists.

        Lazy creation rule: Only creates a User when the user's visa.key (public key)
        is available (entity is "ready" for use). Does not cache the created user automatically.

        :param identifier: user ID
        :return: user, None on not ready
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.create_user()'
        )

    @abstractmethod
    def create_group(self, identifier: ID) -> Optional[Group]:
        """
        Creates a Group entity if the required member list exists.

        Lazy creation rule: Only creates a Group when the group's member list is available
        (entity is "ready" for use). Does not cache the created group automatically.

        :param identifier: group ID
        :return: group, None on not ready
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.create_group()'
        )

    #
    #   Local Users
    #

    @abstractmethod
    async def get_local_users(self) -> List[ID]:
        """
        Retrieves all local user IDs (used for decrypting received messages).

        Local users are accounts logged into the current device with private keys,
        required to decrypt incoming personal/group messages targeted to the device.

        :return: users with private key
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.get_local_users()'
        )
