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

from dimp import EntityType, ID
from dimp import User, Group
from dimp import Meta, Document
from dimp import Barrack
from dimp import BaseUser, BaseGroup

from .mkm import ServiceProvider, Station, Bot


class Facebook(Barrack, ABC):

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

    # Override
    def create_user(self, identifier: ID) -> Optional[User]:
        assert identifier.is_user, 'user ID error: %s' % identifier
        # check visa key
        if not identifier.is_broadcast:
            if self.public_key_for_encryption(identifier=identifier) is None:
                # assert False, 'visa.key not found: %s' % identifier
                return None
            # NOTICE: if visa.key exists, then visa & meta must exist too.
        network = identifier.type
        # check user type
        if network == EntityType.STATION:
            return Station(identifier=identifier)
        elif network == EntityType.BOT:
            return Bot(identifier=identifier)
        # general user, or 'anyone@anywhere'
        return BaseUser(identifier=identifier)

    # Override
    def create_group(self, identifier: ID) -> Optional[Group]:
        assert identifier.is_group, 'group ID error: %s' % identifier
        if not identifier.is_broadcast:
            members = self.members(identifier=identifier)
            if len(members) == 0:
                # assert False, 'group members not found: %s' % identifier
                return None
            # NOTICE: if members exist, then owner (founder) must exist,
            #         and bulletin & meta must exist too.
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
            # not me?
            return None
        # group message (recipient not designated)
        assert receiver.is_group, 'receiver error: %s' % receiver
        # the messenger will check group info before decrypting message,
        # so we can trust that the group's meta & members MUST exist here.
        members = self.members(identifier=receiver)
        assert len(members) > 0, 'members not found: %s' % receiver
        for item in users:
            if item.identifier in members:
                # DISCUSS: set this item to be current user?
                return item
