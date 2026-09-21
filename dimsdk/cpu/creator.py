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

from dimp import ContentType

from ..dkd import ContentProcessor, ContentProcessorCreator

from ..base import TwinsHelper

from .base import BaseContentProcessor
from .base import BaseCommandProcessor


# noinspection PyAbstractClass
class BaseContentProcessorCreator(TwinsHelper, ContentProcessorCreator):
    """Base implementation of :class:`ContentProcessorCreator` for standard content/command types.

    Creates concrete processors for standard commands (meta, documents, ...),
    falling back to base processors for unsupported types/commands.
    """

    # Override
    def create_content_processor(self, msg_type: str) -> Optional[ContentProcessor]:
        # default commands
        if msg_type == ContentType.COMMAND:
            return BaseCommandProcessor(facebook=self.facebook, messenger=self.messenger)

        if msg_type == ContentType.ANY:
            # must return a default processor for type==0
            return BaseContentProcessor(facebook=self.facebook, messenger=self.messenger)
        # assert False, f'unsupported content: {msg_type}'
        return None

    # # Override
    # def create_command_processor(self, msg_type: str, cmd: str) -> Optional[ContentProcessor]:
    #     raise NotImplementedError(
    #         f'Not implemented: {type(self).__module__}.{type(self).__name__}.create_command_processor()'
    #     )
