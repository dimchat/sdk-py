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
from typing import Optional, List

from dimp import ID, Meta, Document

from ..mkm import User, Group


class Barrack(ABC):
    """
        Entity Factory
        ~~~~~~~~~~~~~~
        Entity pool to manage User/Group instances
    """

    @abstractmethod
    def cache_user(self, user: User):
        """ User pool """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.cache_user()'
        )

    @abstractmethod
    def cache_group(self, group: Group):
        """ Group pool """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.cache_group()'
        )

    @abstractmethod
    def get_user(self, identifier: ID) -> Optional[User]:
        """ User factory """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.get_user()'
        )

    @abstractmethod
    def get_group(self, identifier: ID) -> Optional[Group]:
        """ Group factory """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.get_group()'
        )

    @abstractmethod
    def create_user(self, identifier: ID) -> Optional[User]:
        """
        Create user when visa.key exists

        :param identifier: user ID
        :return: user, None on not ready
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.create_user()'
        )

    @abstractmethod
    def create_group(self, identifier: ID) -> Optional[Group]:
        """
        Create group when members exist

        :param identifier: group ID
        :return: group, None on not ready
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.create_group()'
        )


class Archivist(ABC):
    """
        Entity Database
        ~~~~~~~~~~~~~~~
    """

    @abstractmethod
    async def save_meta(self, meta: Meta, identifier: ID) -> bool:
        """
        Save meta for entity ID (must verify first)

        :param meta:       entity meta
        :param identifier: entity ID
        :return: True on success
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.save_meta()'
        )

    @abstractmethod
    async def save_document(self, document: Document, identifier: ID) -> bool:
        """
        Save entity document with ID (must verify first)

        :param document:   entity document
        :param identifier: entity ID
        :return: True on success
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.save_document()'
        )

    #
    #   Local Users
    #

    @abstractmethod
    async def get_local_users(self) -> List[ID]:
        """
        Get all local users (for decrypting received message)

        :return: users with private key
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.get_local_users()'
        )
