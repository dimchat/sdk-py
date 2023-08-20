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

from dimp.mkm.address import thanos
from dimp import EntityType, ID
from dimp import User, Group, BaseUser, BaseGroup
from dimp import Meta, Document
from dimp import Barrack

from .mkm import ServiceProvider, Station, Bot


class Facebook(Barrack, ABC):

    def __init__(self):
        super().__init__()
        # memory caches
        self.__users = {}   # ID -> User
        self.__groups = {}  # ID -> Group

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

    # private
    def cache_user(self, user: User):
        if user.data_source is None:
            user.data_source = self
        self.__users[user.identifier] = user

    # private
    def cache_group(self, group: Group):
        if group.data_source is None:
            group.data_source = self
        self.__groups[group.identifier] = group

    @abstractmethod
    def save_meta(self, meta: Meta, identifier: ID) -> bool:
        """
        Save meta for entity ID (must verify first)

        :param meta:       entity meta
        :param identifier: entity ID
        :return: True on success
        """
        raise NotImplemented

    @abstractmethod
    def save_document(self, document: Document) -> bool:
        """
        Save entity document with ID (must verify first)

        :param document: entity document
        :return: True on success
        """
        raise NotImplemented

    #
    #   Document checking
    #
    def check_document(self, document: Document) -> bool:
        """
        Checking document

        :param document: entity document
        :return: True on accepted
        """
        identifier = document.identifier
        # NOTICE: if this is a bulletin document for group,
        #             verify it with the group owner's meta.key
        #         else (this is a visa document for user)
        #             verify it with the user's meta.key
        if identifier.is_group:
            # check by group owner's meta.key
            owner = self.owner(identifier=identifier)
            if owner is not None:
                meta = self.meta(identifier=owner)
            elif identifier.type == EntityType.GROUP:
                # NOTICE: if this is a polylogue profile
                #             verify it with the founder's meta.key
                #             (which equals to the group's meta.key)
                meta = self.meta(identifier=identifier)
            else:
                # FIXME: owner not found for this group
                return False
        else:
            # check by user's meta.key
            meta = self.meta(identifier=identifier)
        if meta is not None:
            return document.verify(public_key=meta.key)

    # protected
    # noinspection PyMethodMayBeStatic
    def create_user(self, identifier: ID) -> Optional[User]:
        # TODO: make sure visa key exists before calling this
        network = identifier.type
        # check user type
        if network == EntityType.STATION:
            # TODO: get station ip,port before create it
            # return Station(identifier=identifier, host='0.0.0.0', port=0)
            return Station(identifier=identifier)
        elif network == EntityType.BOT:
            return Bot(identifier=identifier)
        # general user, or 'anyone@anywhere'
        return BaseUser(identifier=identifier)

    # protected
    # noinspection PyMethodMayBeStatic
    def create_group(self, identifier: ID) -> Optional[Group]:
        # TODO: make group meta exists before calling this
        network = identifier.type
        # check group type
        if network == EntityType.ISP:
            return ServiceProvider(identifier=identifier)
        # general group, or 'everyone@everywhere'
        return BaseGroup(identifier=identifier)

    @property
    @abstractmethod
    def local_users(self) -> List[User]:
        """
        Get all local users (for decrypting received message)

        :return: users with private key
        """
        raise NotImplemented

    def select_user(self, receiver: ID) -> Optional[User]:
        """ Select local user for receiver """
        users = self.local_users
        if len(users) == 0:
            assert False, 'local users should not be empty'
            # return None
        elif receiver.is_broadcast:
            # broadcast message can decrypt by anyone, so just return current user
            return users[0]
        elif receiver.is_user:
            # 1. personal message
            # 2. split group message
            for item in users:
                if item.identifier == receiver:
                    # DISCUSS: set this item to be current user?
                    return item
            # not mine?
            return None
        # group message (recipient not designated)
        assert receiver.is_group, 'receiver error: %s' % receiver
        # the messenger will check group info before decrypting message,
        # so we can trust that the group's meta & members MUST exist here.
        grp = self.group(identifier=receiver)
        if grp is None:
            assert False, 'group not ready: %s' % receiver
            # return None
        members = grp.members
        assert len(members) > 0, 'members not found: %s' % receiver
        for item in users:
            if item.identifier in members:
                # DISCUSS: set this item to be current user?
                return item

    #
    #   Entity Delegate
    #

    # Override
    def user(self, identifier: ID) -> Optional[User]:
        # 1. get from user cache
        usr = self.__users.get(identifier)
        if usr is None:
            # 2. create and cache it
            usr = self.create_user(identifier=identifier)
            if usr is not None:
                self.cache_user(user=usr)
        return usr

    # Override
    def group(self, identifier: ID) -> Optional[Group]:
        # 1. get from group cache
        grp = self.__groups.get(identifier)
        if grp is None:
            # 2. create and cache it
            grp = self.create_group(identifier=identifier)
            if grp is not None:
                self.cache_group(group=grp)
        return grp
