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

from dimp import ReliableMessage
from dimp import Content, Command

from ..core import TwinsHelper
from ..core import ContentProcessor

from ..facebook import Facebook
from ..messenger import Messenger


class BaseContentProcessor(TwinsHelper, ContentProcessor):
    """
        Content Processing Unit
        ~~~~~~~~~~~~~~~~~~~~~~~
    """

    @property
    def facebook(self) -> Optional[Facebook]:
        barrack = super().facebook
        assert isinstance(barrack, Facebook), 'barrack error: %s' % barrack
        return barrack

    @property
    def messenger(self) -> Optional[Messenger]:
        transceiver = super().messenger
        assert isinstance(transceiver, Messenger), 'transceiver error: %s' % transceiver
        return transceiver

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


class BaseCommandProcessor(BaseContentProcessor):
    """
        Command Processing Unit
        ~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Override
    async def process_content(self, content: Content, r_msg: ReliableMessage) -> List[Content]:
        assert isinstance(content, Command), 'command error: %s' % content
        text = 'Command not support.'
        return self._respond_receipt(text=text, envelope=r_msg.envelope, content=content, extra={
            'template': 'Command (name: ${command}) not support yet!',
            'replacements': {
                'command': content.cmd,
            }
        })
