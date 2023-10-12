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
    Processor Factory
    ~~~~~~~~~~~~~~~~~

    produce content/command processors
"""

from typing import Optional

from dimp import ContentType, Command

from ..core import TwinsHelper
from ..core import ContentProcessor, ContentProcessorCreator

# from .base import BaseContentProcessor
from .base import BaseCommandProcessor

from .contents import ForwardContentProcessor
from .contents import ArrayContentProcessor
# from .customized import CustomizedContentProcessor
from .commands import MetaCommandProcessor
from .commands import DocumentCommandProcessor


class BaseContentProcessorCreator(TwinsHelper, ContentProcessorCreator):
    """ Base ContentProcessor Creator """

    # Override
    def create_content_processor(self, msg_type: int) -> Optional[ContentProcessor]:
        # forward content
        if msg_type == ContentType.FORWARD.value:
            return ForwardContentProcessor(facebook=self.facebook, messenger=self.messenger)
        # array content
        if msg_type == ContentType.ARRAY.value:
            return ArrayContentProcessor(facebook=self.facebook, messenger=self.messenger)

        # # application customized
        # if msg_type == ContentType.APPLICATION.value:
        #     return CustomizedContentProcessor(facebook=self.facebook, messenger=self.messenger)
        # elif msg_type == ContentType.CUSTOMIZED.value:
        #     return CustomizedContentProcessor(facebook=self.facebook, messenger=self.messenger)

        # group commands
        if msg_type == ContentType.COMMAND.value:
            return BaseCommandProcessor(facebook=self.facebook, messenger=self.messenger)

        # # default contents
        # if msg_type == 0:
        #     return BaseContentProcessor(facebook=self.facebook, messenger=self.messenger)

    # Override
    def create_command_processor(self, msg_type: int, cmd: str) -> Optional[ContentProcessor]:
        # meta command
        if cmd == Command.META:
            return MetaCommandProcessor(facebook=self.facebook, messenger=self.messenger)
        # document command
        if cmd == Command.DOCUMENT:
            return DocumentCommandProcessor(facebook=self.facebook, messenger=self.messenger)
