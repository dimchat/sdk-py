# -*- coding: utf-8 -*-
#
#   DIM-SDK : Decentralized Instant Messaging Software Development Kit
#
#                                Written in 2020 by Moky <albert.moky@gmail.com>
#
# ==============================================================================
# MIT License
#
# Copyright (c) 2020 Albert Moky
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
from abc import ABC
from typing import Optional

from dimp import ID
from dimp import Content, Envelope, InstantMessage

from .messenger import Messenger, Callback
from .facebook import Facebook


class MessageTransmitter(Messenger.Transmitter, ABC):

    def __init__(self, messenger: Messenger):
        super().__init__()
        self.__messenger = weakref.ref(messenger)

    @property
    def messenger(self) -> Messenger:
        return self.__messenger()

    @property
    def facebook(self) -> Facebook:
        return self.messenger.facebook

    def send_content(self, sender: ID, receiver: ID, content: Content,
                     callback: Optional[Callback] = None, priority: int = 0) -> bool:
        if sender is None:
            # Application Layer should make sure user is already login before it send message to server.
            # Application layer should put message into queue so that it will send automatically after user login
            user = self.facebook.current_user
            assert user is not None, 'failed to get current user'
            sender = user.identifier
        # pack and send
        env = Envelope.create(sender=sender, receiver=receiver)
        msg = InstantMessage.create(head=env, body=content)
        return self.messenger.send_instant_message(msg=msg, callback=callback, priority=priority)

    def send_instant_message(self, msg: InstantMessage,
                             callback: Optional[Callback] = None, priority: int = 0) -> bool:
        messenger = self.messenger
        # Send message (secured + certified) to target station
        s_msg = messenger.encrypt_message(msg=msg)
        if s_msg is None:
            # public key not found?
            # raise AssertionError('failed to encrypt message: %s' % msg)
            return False
        r_msg = messenger.sign_message(msg=s_msg)
        if r_msg is None:
            # TODO: set iMsg.state = error
            raise AssertionError('failed to sign message: %s' % s_msg)
        # TODO: if OK, set iMsg.state = sending; else set iMsg.state = waiting
        return messenger.send_reliable_message(msg=r_msg, callback=callback, priority=priority)
