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
from dimp import InstantMessage
from dimp import ContentType, Content
from dimp import Command

from .processor import ContentProcessor


class CommandProcessor(ContentProcessor):

    def __init__(self, context: dict):
        super().__init__(context=context)
        # sub-command processing units pool
        self.__pool = {}

    #
    #   Runtime
    #
    __command_processor_classes = {}  # class map

    @classmethod
    def register(cls, command: str, processor_class=None) -> bool:
        if processor_class is None:
            cls.__command_processor_classes.pop(command, None)
        elif issubclass(processor_class, CommandProcessor):
            cls.__command_processor_classes[command] = processor_class
        else:
            raise TypeError('%s must be subclass of CommandProcessor' % processor_class)
        return True

    @classmethod
    def cpu_class(cls, command: str):
        clazz = cls.__command_processor_classes.get(command)
        if clazz is not None:
            assert issubclass(clazz, CommandProcessor), 'error: %s, %s' % (command, clazz)
            return clazz

    def cpu(self, command: str):
        processor = self.__pool.get(command)
        if processor is None:
            # try to create new processor with command name
            clazz = self.cpu_class(command=command)
            if clazz is not None:
                processor = clazz(context=self.context)
                self.__pool[command] = processor
        return processor

    #
    #   main
    #
    def process(self, content: Content, sender: ID, msg: InstantMessage) -> Optional[Content]:
        assert isinstance(content, Command), 'command error: %s' % content
        # process command by name
        cpu: CommandProcessor = self.cpu(command=content.command)
        if cpu is not None:
            assert cpu is not self, 'Dead cycle! command: %s' % content
            return cpu.process(content=content, sender=sender, msg=msg)


# register
ContentProcessor.register(content_type=ContentType.Command, processor_class=CommandProcessor)
