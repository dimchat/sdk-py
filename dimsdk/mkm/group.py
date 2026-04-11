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

from dimp import ID

from .entity import EntityDataSource, Entity, BaseEntity


class GroupDataSource(EntityDataSource, ABC):
    """ This interface is for getting information for group

        Group Data Source
        ~~~~~~~~~~~~~~~~~

        1. founder has the same public key with the group's meta.key
        2. owner and members should be set complying with the consensus algorithm
    """

    @abstractmethod
    async def get_founder(self, identifier: ID) -> Optional[ID]:
        """
        Get founder of the group

        :param identifier: group ID
        :return: founder ID
        """
        raise NotImplemented

    @abstractmethod
    async def get_owner(self, identifier: ID) -> Optional[ID]:
        """
        Get current owner of the group

        :param identifier: group ID
        :return: owner ID
        """
        raise NotImplemented

    @abstractmethod
    async def get_members(self, identifier: ID) -> List[ID]:
        """
        Get all members in the group

        :param identifier: group ID
        :return: member ID list
        """
        raise NotImplemented


class Group(Entity, ABC):
    """ This class is for creating group

        Group for organizing users
        ~~~~~~~~~~~~~~~~~~~~~~~~~~

            roles:
                founder
                owner
                members
                administrators - Optional
                assistants     - group bots
    """

    # @property
    # @abstractmethod
    # def data_source(self) -> Optional[GroupDataSource]:
    #     raise NotImplemented
    #
    # @data_source.setter
    # @abstractmethod
    # def data_source(self, delegate: GroupDataSource):
    #     raise NotImplemented

    @property
    @abstractmethod
    async def founder(self) -> ID:
        raise NotImplemented

    @property
    @abstractmethod
    async def owner(self) -> ID:
        raise NotImplemented

    @property
    @abstractmethod
    async def members(self) -> List[ID]:
        """ NOTICE: the owner must be a member
            (usually the first one) """
        raise NotImplemented


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
            assert isinstance(facebook, GroupDataSource), 'group delegate error: %s' % facebook
            uid = await facebook.get_founder(identifier=self.identifier)
            self.__founder = uid
        return uid

    @property  # Override
    async def owner(self) -> ID:
        facebook = self.data_source
        assert isinstance(facebook, GroupDataSource), 'group delegate error: %s' % facebook
        return await facebook.get_owner(identifier=self.identifier)

    @property  # Override
    async def members(self) -> List[ID]:
        facebook = self.data_source
        assert isinstance(facebook, GroupDataSource), 'group delegate error: %s' % facebook
        return await facebook.get_members(identifier=self.identifier)
