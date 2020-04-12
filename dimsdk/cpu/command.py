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
    Command Processor
    ~~~~~~~~~~~~~~~~~

"""

from typing import Optional

from dimp import ID
from dimp import ReliableMessage
from dimp import ContentType, Content, TextContent
from dimp import Command

from .processor import ContentProcessor


class CommandProcessor(ContentProcessor):

    UNKNOWN = "unknown"

    def __init__(self, messenger):
        super().__init__(messenger=messenger)
        self.__command_processors: dict = {}

    #
    #   Runtime
    #
    __command_processor_classes = {}  # class map

    @classmethod
    def register(cls, command: str, processor_class=None) -> bool:
        if processor_class is None:
            cls.__command_processor_classes.pop(command, None)
        elif processor_class == CommandProcessor:
            raise TypeError('should not add CommandProcessor itself!')
        else:
            assert issubclass(processor_class, CommandProcessor), 'cpu class error' % processor_class
            cls.__command_processor_classes[command] = processor_class
        return True

    def cpu(self, command: str):
        # 1. get from pool
        processor = self.__command_processors.get(command)
        if processor is not None:
            return processor
        # 2. get CPU class by command name
        clazz = self.__command_processor_classes.get(command)
        if clazz is None:
            if command == self.UNKNOWN:
                raise LookupError('default CPU not set yet')
            # call default CPU
            return self.cpu(command=self.UNKNOWN)
        # 3. create CPU with messenger
        processor = self._create_processor(clazz)
        assert processor is not None, 'failed to create CPU for command: %s' % command
        self.__command_processors[command] = processor
        return processor

    #
    #   main
    #
    def process(self, content: Content, sender: ID, msg: ReliableMessage) -> Optional[Content]:
        assert type(self) == CommandProcessor, 'override me!'
        assert isinstance(content, Command), 'command error: %s' % content
        # process command by name
        cpu = self.cpu(command=content.command)
        assert cpu is not self, 'Dead cycle! command: %s' % content
        return cpu.process(content=content, sender=sender, msg=msg)


#
#   Default Command Processor
#
class _DefaultCommandProcessor(CommandProcessor):

    #
    #   main
    #
    def process(self, content: Content, sender: ID, msg: ReliableMessage) -> Content:
        assert isinstance(content, Command), 'command error: %s' % content
        res = TextContent.new(text='Command (name: %s) not support yet!' % content.command)
        # check group message
        group = content.group
        if group is not None:
            res.group = group
        return res


# register
ContentProcessor.register(content_type=ContentType.Command, processor_class=CommandProcessor)
CommandProcessor.register(command=CommandProcessor.UNKNOWN, processor_class=_DefaultCommandProcessor)
