# -*- coding: utf-8 -*-
#
#   DIMP : Decentralized Instant Messaging Protocol
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

from abc import ABC
from typing import Optional, Dict

from dimp import ID

from ..mkm import EntityDelegate
from ..mkm import User, Group


class Barrack(EntityDelegate, ABC):
    """
        Entity Factory
        ~~~~~~~~~~~~~~
        Entity pool to manage User/Group instances
    """

    def __init__(self):
        super().__init__()
        # memory caches
        self.__users: Dict[ID, User] = {}    # ID -> User
        self.__groups: Dict[ID, Group] = {}  # ID -> Group

    # protected
    def cache_user(self, user: User):
        self.__users[user.identifier] = user

    # protected
    def cache_group(self, group: Group):
        self.__groups[group.identifier] = group

    #
    #   Entity Delegate
    #

    # Override
    async def get_user(self, identifier: ID) -> Optional[User]:
        return self.__users.get(identifier)

    # Override
    async def get_group(self, identifier: ID) -> Optional[Group]:
        return self.__groups.get(identifier)

    #
    #   Garbage Collection
    #

    def reduce_memory(self) -> int:
        """
        Call it when received 'UIApplicationDidReceiveMemoryWarningNotification',
        this will remove 50% of cached objects

        :return: number of survivors
        """
        finger = 0
        finger = thanos(self.__users, finger)
        finger = thanos(self.__groups, finger)
        return finger >> 1


def thanos(planet: dict, finger: int) -> int:
    """ Thanos can kill half lives of a world with a snap of the finger """
    people = planet.keys()
    for anybody in people:
        if (++finger & 1) == 1:
            # kill it
            planet.pop(anybody)
    return finger
