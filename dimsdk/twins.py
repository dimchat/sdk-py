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

from .mkm import User

from .facebook import Facebook
from .messenger import Messenger


class TwinsHelper:
    """
        Messenger Shadow
        ~~~~~~~~~~~~~~~~

        Delegate for Messenger
    """

    def __init__(self, facebook: Facebook, messenger: Messenger):
        super().__init__()
        self.__facebook = weakref.ref(facebook)
        self.__messenger = weakref.ref(messenger)

    @property
    def facebook(self) -> Optional[Facebook]:
        return self.__facebook()

    @property
    def messenger(self) -> Optional[Messenger]:
        return self.__messenger()

    # protected
    async def select_local_user(self, receiver: ID) -> Optional[User]:
        """ Selects the local User entity for decrypting messages to a target receiver """
        facebook = self.facebook
        assert facebook is not None, 'facebook not ready'
        if receiver.is_broadcast:
            # broadcast message can be decrypted by anyone
            me = await facebook.select_user(receiver=receiver)
        elif receiver.is_user:
            # check local users
            me = await facebook.select_user(receiver=receiver)
        elif receiver.is_group:
            members = await facebook.get_members(identifier=receiver)
            if members is None or len(members) == 0:
                # assert False, 'failed to get group members: %s' % receiver
                return None
            me = await facebook.select_member(members=members)
        else:
            assert False, 'unknown receiver: %s' % receiver
        if me is None:
            # not for me?
            return None
        return await facebook.get_user(identifier=me)
