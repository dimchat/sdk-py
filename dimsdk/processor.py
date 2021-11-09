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

from typing import List, Union, Optional

from dimp import ContentType, Content, ReliableMessage
from dimp import Processor

from .cpu import ContentProcessor, CommandProcessor
from .cpu import ProcessorFactory
from .messenger import Messenger


class MessageProcessor(Processor):

    def __init__(self, messenger: Messenger):
        super().__init__(transceiver=messenger)
        self.__cpm = self._create_processor_factory()

    # protected
    def _create_processor_factory(self) -> ProcessorFactory:
        return ProcessorFactory(messenger=self.messenger)

    def get_processor(self, content: Content) -> Optional[ContentProcessor]:
        return self.__cpm.get_processor(content=content)

    def get_processor_by_type(self, msg_type: Union[int, ContentType]) -> Optional[ContentProcessor]:
        return self.__cpm.get_content_processor(msg_type=msg_type)

    def get_processor_by_name(self, cmd_name: str, msg_type: Union[int, ContentType] = 0) -> Optional[CommandProcessor]:
        return self.__cpm.get_command_processor(msg_type=msg_type, cmd_name=cmd_name)

    @property
    def messenger(self) -> Messenger:
        transceiver = self.transceiver
        assert isinstance(transceiver, Messenger), 'messenger error: %s' % transceiver
        return transceiver

    def process_content(self, content: Content, r_msg: ReliableMessage) -> List[Content]:
        # TODO: override to check group
        cpu = self.get_processor(content=content)
        return cpu.process(content=content, msg=r_msg)
        # TODO: override to filter the response
