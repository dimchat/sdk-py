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

from dimp import ID

from ..core import Barrack, Archivist
from ..mkm import EntityDelegate, User, Group
from ..mkm import UserDataSource, GroupDataSource


class Facebook(EntityDelegate, UserDataSource, GroupDataSource, ABC):

    @property  # protected
    @abstractmethod
    def barrack(self) -> Optional[Barrack]:
        """ Entity factory """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.barrack getter'
        )

    @property
    @abstractmethod
    def archivist(self) -> Optional[Archivist]:
        """ Entity database """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.archivist getter'
        )

    async def select_user(self, receiver: ID) -> Optional[ID]:
        """
        Select local user for receiver

        :param receiver: user/broadcast ID
        :return: local user
        """
        assert receiver.is_user or receiver.is_broadcast, 'user ID error: %s' % receiver
        archivist = self.archivist
        assert archivist is not None, 'archivist not ready'
        all_users = await archivist.get_local_users()
        if all_users is None or len(all_users) == 0:
            # assert False, 'local users should not be empty'
            return None
        elif receiver.is_broadcast:
            # broadcast message can decrypt by anyone, so
            # just return current user
            return all_users[0]
        # personal message
        for item in all_users:
            if receiver == item:
                # DISCUSS: set this item to be current user?
                return item
        # not for me?

    async def select_member(self, members: List[ID]) -> Optional[ID]:
        """
        Select local user for group members

        :param members: group member list
        :return: local user
        """
        archivist = self.archivist
        assert archivist is not None, 'archivist not ready'
        all_users = await archivist.get_local_users()
        if all_users is None or len(all_users) == 0:
            # assert False, 'local users should not be empty'
            return None
        # group message (recipient not designated)
        for item in all_users:
            if item in members:
                # DISCUSS: set this item to be current user?
                return item
        # not for me?

    #
    #   Entity Delegate
    #

    # Override
    async def get_user(self, identifier: ID) -> Optional[User]:
        assert identifier.is_user, 'user ID error: %s' % identifier
        barrack = self.barrack
        assert barrack is not None, 'barrack not ready'
        # get from user cache
        user = barrack.get_user(identifier=identifier)
        if user is None:
            # create user and cache it
            user = barrack.create_user(identifier=identifier)
            if user is not None:
                barrack.cache_user(user=user)
        return user

    # Override
    async def get_group(self, identifier: ID) -> Optional[Group]:
        assert identifier.is_group, 'group ID error: %s' % identifier
        barrack = self.barrack
        assert barrack is not None, 'barrack not ready'
        # get from group cache
        group = barrack.get_group(identifier=identifier)
        if group is None:
            # create group and cache it
            group = barrack.create_group(identifier=identifier)
            if group is not None:
                barrack.cache_group(group=group)
        return group
