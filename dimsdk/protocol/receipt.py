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

"""
    Receipt Protocol
    ~~~~~~~~~~~~~~~~

    As receipt returned to sender to proofing the message's received
"""

from typing import Optional

from dimp import Envelope
from dimp import Command


class ReceiptCommand(Command):
    """
        Receipt Command
        ~~~~~~~~~~~~~~~

        data format: {
            type : 0x88,
            sn   : 123,

            command  : "receipt", // command name
            message  : "...",
            //-- extra info
            sender   : "...",
            receiver : "...",
            time     : 0
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

    # -------- setters/getters

    @property
    def message(self) -> Optional[str]:
        return self.get('message')

    @property
    def envelope(self) -> Optional[Envelope]:
        if self.__envelope is None:
            # envelope: { sender: "...", receiver: "...", time: 0 }
            env = self.get('envelope')
            if env is None and 'sender' in self and 'receiver' in self:
                env = self
            if env is not None:
                self.__envelope = Envelope(env)
                self.__envelope.delegate = self.delegate
        return self.__envelope

    #
    #   Factories
    #
    @classmethod
    def new(cls, content: dict=None, message: str=None, sn: int=0, envelope: Envelope=None):
        """
        Create receipt command

        :param content:  command info
        :param message:  receipt message
        :param sn:       serial number of the message responding to
        :param envelope: envelope of the message responding to
        :return: ReceiptCommand object
        """
        if content is None:
            # create empty content
            content = {}
        # set receipt message
        if message is not None:
            content['message'] = message
        # set sn for the message responding to
        if sn > 0:
            content['sn'] = sn
        # set envelope for the message responding to
        if envelope is not None:
            content['sender'] = envelope.sender
            content['receiver'] = envelope.receiver
            content['time'] = envelope.time
            # TODO: envelope.group?
        # new ReceiptCommand(dict)
        return super().new(content=content, command=Command.RECEIPT)


# register command class
Command.register(command=Command.RECEIPT, command_class=ReceiptCommand)
