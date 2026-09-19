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

from ..core import Barrack
from ..mkm import EntityDelegate, User, Group
from ..mkm import UserDataSource, GroupDataSource


class Facebook(EntityDelegate, UserDataSource, GroupDataSource, ABC):
    """Unified manager for user/group entity operations (combines caching + data access).

    Implements core entity management workflows:
    1. Selects the correct local user for message decryption
    2. Retrieves/creates user/group entities (combines Barrack cache + lazy creation)
    3. Integrates with Archivist for persistent data access

    Implements: :class:`EntityDelegate`, :class:`UserDataSource`, :class:`GroupDataSource`
    """

    @property  # protected
    @abstractmethod
    def barrack(self) -> Optional[Barrack]:
        """Returns the entity cache manager (Barrack) - internal use only.

        None if the barrack is not initialized/ready for use.
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.barrack getter'
        )

    #
    #   Entity Delegate
    #

    async def select_user(self, receiver: ID) -> Optional[ID]:
        """Selects a local user for decrypting messages to a user/broadcast receiver.

        Core logic:
          0. Validates receiver type (only user/broadcast allowed)
          1. If receiver is broadcast -> returns first local user (any user can decrypt)
          2. If receiver is user -> returns matching local user (personal message target)
          3. Returns None if no matching local user is found

        `receiver` is the target receiver ID (must be user or broadcast type).

        Returns a local user ID for decryption (None if no match).

        Raises an assertion error if receiver is invalid (group) or local users are empty.

        :param receiver: user/broadcast ID
        :return: local user
        """
        assert receiver.is_user or receiver.is_broadcast, f'user ID error: {receiver}'
        archivist = self.barrack
        assert archivist is not None, 'archivist not ready'
        all_users = await archivist.get_local_users()
        if all_users is None or len(all_users) == 0:
            # assert False, 'local users should not be empty'
            return None
        elif receiver.is_broadcast:
            # broadcast message can be decrypted by anyone, so
            # just return current user here
            return all_users[0]
        # personal message
        for item in all_users:
            if receiver.is_same_as(other=item):
                # DISCUSS: set this item to be current user?
                return item
        # not for me?

    async def select_member(self, members: List[ID]) -> Optional[ID]:
        """Selects a local user who is a member of a specific group (for group message decryption).

        Core logic:
          0. Validates group member list is non-empty
          1. Finds the first local user that exists in the group member list
          2. Returns None if no local user is a group member

        `members` is the list of group member IDs (must be non-empty).

        Returns a local user ID who is a group member (None if no match).

        Raises an assertion error if members are empty or local users are empty.

        :param members: group member list
        :return: local user
        """
        assert members is not None and len(members) > 0, 'group members not found'
        archivist = self.barrack
        assert archivist is not None, 'archivist not ready'
        all_users = await archivist.get_local_users()
        if all_users is None or len(all_users) == 0:
            # assert False, 'local users should not be empty'
            return None
        # group message (recipient not designated)
        for item in all_users:
            for did in members:
                if did.is_same_as(other=item):
                    # DISCUSS: set this item to be current user?
                    return item
        # not for me?

    #
    #   Entity Delegate
    #

    # Override
    async def get_user(self, identifier: ID) -> Optional[User]:
        assert identifier.is_user, f'user ID error: {identifier}'
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
        assert identifier.is_group, f'group ID error: {identifier}'
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
