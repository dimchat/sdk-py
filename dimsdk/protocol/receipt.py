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
    Receipt Protocol
    ~~~~~~~~~~~~~~~~

    As receipt returned to sender to proofing the message's received
"""

from dimp import Envelope
from dimp import Command
from dimp.protocol.command import command_classes
from mkm.crypto.utils import base64_decode


class ReceiptCommand(Command):
    """
        Receipt Command
        ~~~~~~~~~~~~~~~

        data format: {
            type : 0x88,
            sn   : 123,

            command : "receipt", // command name
            message : "...",
            //-- extra info
            // 1. envelope
            // 2. signature
        }
    """

    def __new__(cls, cmd: dict):
        """
        Create receipt command

        :param cmd: command info
        :return: ReceiptCommand object
        """
        if cmd is None:
            return None
        elif cls is ReceiptCommand:
            if isinstance(cmd, ReceiptCommand):
                # return ReceiptCommand object directly
                return cmd
        # new ReceiptCommand(dict)
        return super().__new__(cls, cmd)

    def __init__(self, content: dict):
        if self is content:
            # no need to init again
            return
        super().__init__(content)
        # lazy
        self.__envelope: Envelope = None
        self.__signature: bytes = None

    #
    #   envelope
    #
    @property
    def envelope(self) -> Envelope:
        if self.__envelope is None:
            if 'sender' in self and 'receiver' in self:
                self.__envelope = Envelope(self)
        return self.__envelope

    #
    #   signature
    #
    @property
    def signature(self) -> bytes:
        if self.__signature is None:
            base64 = self.get('signature')
            if base64 is not None:
                self.__signature = base64_decode(base64)
        return self.__signature

    #
    #   message
    #
    @property
    def message(self) -> str:
        return self.get('message')

    @message.setter
    def message(self, value: str):
        if value is None:
            self.pop('message', None)
        else:
            self['message'] = value

    #
    #   Factories
    #
    @classmethod
    def new(cls, content: dict=None, message: str=None):
        """
        Create receipt command

        :param content: command info
        :param message: receipt message
        :return: ReceiptCommand object
        """
        if content is None:
            # create empty content
            content = {}
        # set receipt message
        if message is not None:
            content['message'] = message
        # new ReceiptCommand(dict)
        return super().new(content=content, command=Command.RECEIPT)


# register command class
command_classes[Command.RECEIPT] = ReceiptCommand
