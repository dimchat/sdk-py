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
    Core Entity Interfaces (User/Group Base)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import weakref
from abc import ABC, abstractmethod
from typing import Optional, List

from dimp import ID, Meta, Document


class EntityDataSource(ABC):
    """Data source interface for retrieving entity metadata and documents.

    Defines the contract for fetching core entity data, enabling separation of data storage
    (local database, remote API) from entity logic.

    Key data responsibilities:
    1. User Meta: Generated from the user's private key (contains public key for verification)
    2. Group Meta: Generated from the group founder's private key
    3. Meta Public Key: Used to verify messages sent by the user/group founder
    4. Visa Public Key: Used to encrypt messages for the user (terminal-specific)
    """

    @abstractmethod
    async def get_meta(self, identifier: ID) -> Optional[Meta]:
        """
        Get meta for entity

        :param identifier: entity ID
        :return: Meta object
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.get_meta()'
        )

    @abstractmethod
    async def get_documents(self, identifier: ID) -> List[Document]:
        """
        Get documents for entity ID

        :param identifier: entity ID
        :return: Document list
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.get_documents()'
        )


class Entity(ABC):
    """Base interface for all network entities (User/Group).

    Defines the core properties and data access patterns for entities in the communication system.
    Entities are identified by a unique ID and have associated metadata (Meta) and extended documents
    (e.g., Visa for Users, Bulletin for Groups).

    Core properties:
    - ``identifier`` : Unique ID of the entity (user/group ID)
    - ``type``       : Numeric type identifier for the entity (user = 0, group = 1, etc.)
    - ``meta``       : Cryptographic metadata used to generate the entity ID
    - ``documents``  : Extended information (Visa for users, Bulletin for groups)
    """

    @property
    @abstractmethod
    def data_source(self) -> Optional[EntityDataSource]:
        """Data source delegate for retrieving entity data (Meta/Documents).

        If set, the entity will use this delegate to fetch metadata and documents instead of
        internal implementation, enabling flexible data sourcing (local/remote).
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.data_source getter'
        )

    @data_source.setter
    @abstractmethod
    def data_source(self, facebook: EntityDataSource):
        """ Set entity database """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.data_source setter'
        )

    @property
    @abstractmethod
    def identifier(self) -> ID:
        """Unique identifier of the entity (user/group ID).

        Serves as the primary key for identifying the entity in the system.
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.identifier getter'
        )

    @property
    @abstractmethod
    def type(self) -> int:
        """Numeric type identifier of the entity (EntityType).

        Common values:
        - 0 : User entity
        - 1 : Group entity
        - ...
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.type getter'
        )

    @property
    @abstractmethod
    async def meta(self) -> Meta:
        """Cryptographic metadata of the entity (async).

        Contains the core public key and type information used to generate the entity's ID.
        Fetched from ``data_source`` if available, otherwise from internal storage.

        Returns the entity's core Meta object.
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.meta getter'
        )

    @property
    @abstractmethod
    async def documents(self) -> List[Document]:
        """Extended documents associated with the entity (async).

        - For users: Contains :class:`Visa` documents (identity/authorization info with terminal data)
        - For groups: Contains :class:`Bulletin` documents (group info/announcements)

        Returns the list of entity documents (empty list if none).
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.documents getter'
        )


class BaseEntity(Entity):

    def __init__(self, identifier: ID):
        """
        Create Entity with ID

        :param identifier: User/Group ID
        """
        super().__init__()
        self.__id = identifier
        self.__facebook = None

    # Override
    def __str__(self):
        """ Return str(self). """
        clazz = self.__class__.__name__
        identifier = self.identifier
        network = identifier.address.network
        return f'<{clazz} id="{identifier}" network={network} />'

    # Override
    def __eq__(self, other) -> bool:
        """ Return self==value. """
        if isinstance(other, Entity):
            if self is other:
                # same object
                return True
            other = other.identifier
        # check with ID
        return self.__id.__eq__(other)

    # Override
    def __ne__(self, other) -> bool:
        """ Return self!=value. """
        if isinstance(other, Entity):
            if self is other:
                # same object
                return False
            other = other.identifier
        # check with ID
        return self.__id.__ne__(other)

    # Override
    def __hash__(self) -> int:
        return hash(self.__id)

    @property  # Override
    def data_source(self) -> Optional[EntityDataSource]:
        facebook = self.__facebook
        if facebook is not None:
            return facebook()

    @data_source.setter  # Override
    def data_source(self, facebook: EntityDataSource):
        if facebook is None:
            self.__facebook = None
        else:
            self.__facebook = weakref.ref(facebook)

    @property  # Override
    def identifier(self) -> ID:
        return self.__id

    @property  # Override
    def type(self) -> int:
        """ Entity type """
        return self.__id.type

    @property  # Override
    async def meta(self) -> Meta:
        delegate = self.data_source
        assert delegate is not None, 'entity data source not set yet'
        return await delegate.get_meta(identifier=self.__id)

    @property  # Override
    async def documents(self) -> List[Document]:
        delegate = self.data_source
        assert delegate is not None, 'entity data source not set yet'
        return await delegate.get_documents(identifier=self.__id)
