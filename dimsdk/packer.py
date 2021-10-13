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

from typing import Optional

from dimp import InstantMessage, SecureMessage, ReliableMessage
from dimp import Packer

from .facebook import Facebook
from .messenger import Messenger


class MessagePacker(Packer):

    def __init__(self, messenger: Messenger):
        super().__init__(transceiver=messenger)

    @property
    def messenger(self) -> Messenger:
        transceiver = self.transceiver
        assert isinstance(transceiver, Messenger), 'messenger error: %s' % transceiver
        return transceiver

    @property
    def facebook(self) -> Facebook:
        return self.messenger.facebook

    def verify_message(self, msg: ReliableMessage) -> Optional[SecureMessage]:
        facebook = self.facebook
        sender = msg.sender
        # [Meta Protocol]
        meta = msg.meta
        if meta is not None:
            facebook.save_meta(meta=meta, identifier=sender)
        # [Visa Protocol]
        visa = msg.visa
        if visa is not None:
            facebook.save_document(document=visa)
        # make sure meta exists before verifying message
        return super().verify_message(msg=msg)

    def decrypt_message(self, msg: SecureMessage) -> Optional[InstantMessage]:
        if msg.delegate is None:
            msg.delegate = self.transceiver
        receiver = msg.receiver
        user = self.messenger.select_user(receiver=receiver)
        if user is None:
            # current users not match
            trimmed = None
        elif receiver.is_group:
            # trim group message
            trimmed = msg.trim(member=user.identifier)
        else:
            trimmed = msg
        if trimmed is None:
            raise LookupError('receiver error: %s' % msg)
        # make sure private key (decrypt key) exists before decrypting message
        return super().decrypt_message(msg=msg)
