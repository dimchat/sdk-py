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

import weakref
from typing import Optional

from dimp import ID

from ..mkm import User

from .facebook import Facebook
from .messenger import Messenger


class TwinsHelper:
    """Base helper class that provides unified access to Facebook and Messenger dependencies.

    "Twins" refers to the paired core services:
    - **Facebook**: Entity management (user/group metadata, local user selection)
    - **Messenger**: Messaging core (packing/unpacking, encryption/decryption, key management)

    Key design features:
    1. Uses **WeakReference** to hold dependencies, preventing memory leaks (avoids circular references)
    2. Provides a unified entry point for local user selection (critical for message decryption)
    3. Serves as the parent class for all core messaging components (Packer/Processor/ContentProcessor)

    All subclasses inherit access to Facebook/Messenger and the local user selection logic,
    ensuring consistent dependency management across the messaging system.
    """

    def __init__(self, facebook: Facebook, messenger: Messenger):
        """Creates a :class:`TwinsHelper` with references to the core Facebook and Messenger services.

        `facebook` is the entity management service (user/group operations).
        `messenger` is the core messaging service (packing/processing/key management).

        Note: Uses weak references to store dependencies to avoid memory leaks.
        """
        super().__init__()
        self.__facebook = weakref.ref(facebook)
        self.__messenger = weakref.ref(messenger)

    @property
    def facebook(self) -> Optional[Facebook]:
        """Retrieves the Facebook service instance (nullable - may be GC'd).

        Returns the facebook instance (None if garbage collected or not initialized).
        """
        return self.__facebook()

    @property
    def messenger(self) -> Optional[Messenger]:
        """Retrieves the Messenger service instance (nullable - may be GC'd).

        Returns the messenger instance (None if garbage collected or not initialized).
        """
        return self.__messenger()

    # protected
    async def select_local_user(self, receiver: ID) -> Optional[User]:
        """Selects the local User entity for decrypting messages to a target receiver (unified entry).

        Orchestration logic (receiver type routing):
        1. Broadcast receiver -> use `Facebook.select_user` (any local user can decrypt)
        2. User receiver -> use `Facebook.select_user` (matching local user for personal message)
        3. Group receiver ->
           a. Get group members via Facebook (guaranteed to exist per precondition)
           b. Use `Facebook.select_member` (find local user in group member list)
        4. Convert selected user ID to full User entity (via `Facebook.get_user`)

        Precondition: Group member list is guaranteed to exist

        `receiver` is the target receiver ID (supports broadcast/user/group types).

        Returns the local User entity for decryption (None if no matching local user found).

        Raises an assertion error when:
        - Facebook service is unavailable (None)
        - Receiver type is invalid (not broadcast/user/group)
        - Group member list is empty/missing (violates precondition)
        """
        facebook = self.facebook
        assert facebook is not None, 'facebook not ready'
        if receiver.is_broadcast:
            # broadcast message can be decrypted by anyone
            me = await facebook.select_user(receiver=receiver)
        elif receiver.is_user:
            # check local users
            me = await facebook.select_user(receiver=receiver)
        elif receiver.is_group:
            # check local users for the group members
            members = await facebook.get_members(identifier=receiver)
            # the messenger will check group info before decrypting message,
            # so we can trust that the group's meta & members MUST exist here.
            if members is None or len(members) == 0:
                # assert False, f'failed to get group members: {receiver}'
                return None
            me = await facebook.select_member(members=members)
        else:
            assert False, f'unknown receiver: {receiver}'
        if me is None:
            # not for me?
            return None
        return await facebook.get_user(identifier=me)
