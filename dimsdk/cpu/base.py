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
    Content Processor
    ~~~~~~~~~~~~~~~~~

"""

from typing import Optional, List

from dimp import StrMap
from dimp import ReliableMessage
from dimp import Envelope
from dimp import Content, Command

from dimp import CommandHandler, GeneralCommandExtension
from dimp import shared_message_extensions

from ..dkd import ContentProcessor

from ..base import TwinsHelper


# -----------------------------------------------------------------------------
#  BaseContentProcessor (Default CPU Implementation)
# -----------------------------------------------------------------------------


class BaseContentProcessor(TwinsHelper, ContentProcessor):
    """Base implementation of :class:`ContentProcessor` with common response utilities.

    Provides default handling for unsupported content types (returns "not supported" receipt)
    and utility methods for creating receipt responses. Serves as the parent class
    for all concrete content processors.

    Extends :class:`TwinsHelper` to access Facebook (entity management) and Messenger services.
    """

    # Override
    async def process_content(self, content: Content, r_msg: ReliableMessage) -> List[Content]:
        # override to process this content
        text = 'Content not support.'
        return self._respond_receipt(text=text, envelope=r_msg.envelope, content=content, extra={
            'template': 'Content (type: ${type}) not support yet!',
            'replacements': {
                'type': content.type,
            }
        })

    #
    #   Convenient responding
    #

    # protected
    def _respond_receipt(self, text: str, envelope: Envelope, content: Optional[Content],
                         extra: Optional[StrMap] = None) -> List[Content]:
        """Creates a list containing a single receipt command response.

        Convenience method for consistent response formatting across processors.

        `text` is the human-readable response text.
        `envelope` is the original message envelope (for sender/receiver context).
        `content` is the original message content (optional, for additional context).
        `extra` is the extra key-value data to include in the receipt (optional).

        Returns a list with one :class:`ReceiptCommand` instance.
        """
        return [
            self.create_receipt(text=text, envelope=envelope, content=content, extra=extra)
        ]

    @classmethod
    def create_receipt(cls, text: str, envelope: Envelope, content: Optional[Content],
                       extra: Optional[StrMap] = None) -> Command:
        """Creates a receipt command with standardized formatting.

        Includes original message context (envelope, serial number, group ID)
        and optional extra data. Static method for use without instantiation.

        :param text:     respond message
        :param envelope: original message envelope
        :param content:  original message content
        :param extra:    extra info
        :return: receipt command
        """
        # create base receipt command with text, original envelope, serial number & group ID
        helper = command_handler()
        res = helper.create_receipt(text=text, envelope=envelope, content=content)
        # add extra key-values
        if extra is not None:
            res.update(extra)
        return res


def command_extensions() -> GeneralCommandExtension:
    return shared_message_extensions


def command_handler() -> CommandHandler:
    ext = command_extensions()
    return ext.command_handler


# -----------------------------------------------------------------------------
#  BaseCommandProcessor (Default Command CPU)
# -----------------------------------------------------------------------------


class BaseCommandProcessor(BaseContentProcessor):
    """Base implementation of :class:`ContentProcessor` for command content.

    Specializes :class:`BaseContentProcessor` for command handling, providing default
    "command not supported" responses for unsupported commands.
    """

    # Override
    async def process_content(self, content: Content, r_msg: ReliableMessage) -> List[Content]:
        assert isinstance(content, Command), f'command error: {content}'
        text = 'Command not support.'
        return self._respond_receipt(text=text, envelope=r_msg.envelope, content=content, extra={
            'template': 'Command (name: ${command}) not support yet!',
            'replacements': {
                'command': content.cmd,
            }
        })
