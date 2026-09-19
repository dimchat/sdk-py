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
    Group Entity
    ~~~~~~~~~~~~

"""

from abc import ABC, abstractmethod
from typing import Optional, List

from dimp import ID

from .entity import EntityDataSource, Entity, BaseEntity


class GroupDataSource(EntityDataSource, ABC):
    """Data source interface for retrieving group-specific data.

    Extends :class:`EntityDataSource` with group role and membership management, defining
    the contract for fetching group-specific data (founder, owner, members).

    Key rules:
    1. Founder's public key matches the group Meta's public key
    2. Owner/members must be managed according to the system's consensus algorithm
    """

    @abstractmethod
    async def get_founder(self, identifier: ID) -> Optional[ID]:
        """
        Get founder of the group

        :param identifier: group ID
        :return: founder ID
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.get_founder()'
        )

    @abstractmethod
    async def get_owner(self, identifier: ID) -> Optional[ID]:
        """
        Get current owner of the group

        :param identifier: group ID
        :return: owner ID
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.get_owner()'
        )

    @abstractmethod
    async def get_members(self, identifier: ID) -> List[ID]:
        """
        Get all members in the group

        :param identifier: group ID
        :return: member ID list
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.get_members()'
        )


class Group(Entity, ABC):
    """Group entity interface representing a chat group.

    Extends :class:`Entity` with group-specific properties and role management.

    Groups have a hierarchical role structure:
    - Founder        : Original creator of the group (immutable)
    - Owner          : Current administrator of the group (can be transferred)
    - Members        : Regular participants in the group
    - Administrators : Optional role for privileged members (assistants)

    Important note: The group owner must always be a member of the group (usually the first member).
    """

    # @property
    # @abstractmethod
    # def data_source(self) -> Optional[GroupDataSource]:
    #     raise NotImplementedError(
    #         f'Not implemented: {type(self).__module__}.{type(self).__name__}.data_source getter'
    #     )
    #
    # @data_source.setter
    # @abstractmethod
    # def data_source(self, delegate: GroupDataSource):
    #     raise NotImplementedError(
    #         f'Not implemented: {type(self).__module__}.{type(self).__name__}.data_source setter'
    #     )

    @property
    @abstractmethod
    async def founder(self) -> ID:
        """Founder ID of the group (async).

        The original creator of the group (cannot be changed after group creation).
        The founder's private key is used to generate the group's Meta.

        Returns the group founder's ID.
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.founder getter'
        )

    @property
    @abstractmethod
    async def owner(self) -> ID:
        """Current owner ID of the group (async).

        The user with administrative control over the group (can be transferred via abdicate command).
        Must be a member of the group.

        Returns the current group owner's ID.
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.owner getter'
        )

    @property
    @abstractmethod
    async def members(self) -> List[ID]:
        """List of all member IDs in the group (async).

        Includes the owner and all regular members (excludes founder if not a member).

        Returns the list of group member IDs (empty list if none).

        NOTICE: the owner must be a member (usually the first one).
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.members getter'
        )


class BaseGroup(BaseEntity, Group):

    def __init__(self, identifier: ID):
        super().__init__(identifier=identifier)
        # once the group founder is set, it will never change
        self.__founder = None

    @BaseEntity.data_source.getter  # Override
    def data_source(self) -> Optional[GroupDataSource]:
        return super().data_source

    # @data_source.setter  # Override
    # def data_source(self, facebook: GroupDataSource):
    #     super(BaseGroup, BaseGroup).data_source.__set__(self, facebook)

    @property  # Override
    async def founder(self) -> ID:
        uid = self.__founder
        if uid is None:
            facebook = self.data_source
            assert isinstance(facebook, GroupDataSource), f'group data source error: {facebook}'
            uid = await facebook.get_founder(identifier=self.identifier)
            self.__founder = uid
        return uid

    @property  # Override
    async def owner(self) -> ID:
        facebook = self.data_source
        assert isinstance(facebook, GroupDataSource), f'group data source error: {facebook}'
        return await facebook.get_owner(identifier=self.identifier)

    @property  # Override
    async def members(self) -> List[ID]:
        facebook = self.data_source
        assert isinstance(facebook, GroupDataSource), f'group data source error: {facebook}'
        return await facebook.get_members(identifier=self.identifier)
