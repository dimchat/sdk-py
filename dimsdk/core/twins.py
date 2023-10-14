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
from typing import Optional, Dict, List

from dimp import Envelope, Content
from dimp import ReceiptCommand
from dimp import Barrack, Transceiver


class TwinsHelper:
    """
        Messenger Shadow
        ~~~~~~~~~~~~~~~~

        Delegate for Messenger
    """

    def __init__(self, facebook: Barrack, messenger: Transceiver):
        super().__init__()
        self.__facebook = weakref.ref(facebook)
        self.__messenger = weakref.ref(messenger)

    @property
    def facebook(self) -> Barrack:
        return self.__facebook()

    @property
    def messenger(self) -> Transceiver:
        return self.__messenger()

    #
    #   Convenient responding
    #

    def _respond_receipt(self, text: str, envelope: Envelope, content: Optional[Content],
                         extra: Optional[Dict] = None) -> List[ReceiptCommand]:
        return [
            # create base receipt command with text, original envelope, serial number & group ID
            self.create_receipt(text=text, envelope=envelope, content=content, extra=extra)
        ]

    @classmethod
    def create_receipt(cls, text: str, envelope: Envelope, content: Optional[Content],
                       extra: Optional[Dict]) -> ReceiptCommand:
        """
        Receipt command with text, original envelope, serial number & group

        :param text:     respond message
        :param envelope: original message envelope
        :param content:  original message content
        :param extra:    extra info
        :return: receipt command
        """
        res = ReceiptCommand.create(text=text, envelope=envelope, content=content)
        # add extra key-values
        if extra is not None:
            for key in extra:
                res[key] = extra.get(key)
        return res
