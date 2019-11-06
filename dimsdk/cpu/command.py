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
    Command Processors
    ~~~~~~~~~~~~~~~~~~

"""

from dimp import ID
from dimp import InstantMessage
from dimp import ContentType, Content, TextContent
from dimp import Command, HistoryCommand

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
        if clazz is None:
            clazz = cls.__command_processor_classes[DefaultCommandName]
        assert issubclass(clazz, CommandProcessor), 'error: %s, %s' % (command, clazz)
        return clazz

    def cpu(self, command: str):
        processor = self.__pool.get(command)
        if processor is not None:
            return processor
        # try to create new processor with command name
        clazz = self.cpu_class(command=command)
        assert clazz is not None, 'failed to get command processor class: %s' % command
        processor = clazz(context=self.context)
        self.__pool[command] = processor
        return processor

    #
    #   main
    #
    def process(self, content: Content, sender: ID, msg: InstantMessage) -> Content:
        if type(self) != CommandProcessor:
            raise AssertionError('override me!')
        assert isinstance(content, Command), 'command error: %s' % content
        # process command by name
        cpu: CommandProcessor = self.cpu(command=content.command)
        assert cpu is not self, 'Dead cycle! command: %s' % content
        return cpu.process(content=content, sender=sender, msg=msg)


class HistoryCommandProcessor(CommandProcessor):

    def __init__(self, context: dict):
        super().__init__(context=context)
        # lazy
        self.__gpu = None

    def gpu(self):  # GroupCommandProcessor
        if self.__gpu is None:
            from .group import GroupCommandProcessor
            self.__gpu = GroupCommandProcessor(context=self.context)
        return self.__gpu

    #
    #   main
    #
    def process(self, content: Content, sender: ID, msg: InstantMessage) -> Content:
        if type(self) != HistoryCommandProcessor:
            raise AssertionError('override me!')
        assert isinstance(content, Command), 'history error: %s' % content
        if content.group is not None:
            # group command
            return self.gpu().process(content=content, sender=sender, msg=msg)
        # process command by name
        cpu: CommandProcessor = self.cpu(command=content.command)
        assert cpu is not self, 'Dead cycle! history: %s' % content
        return cpu.process(content=content, sender=sender, msg=msg)


# register
ContentProcessor.register(content_type=ContentType.Command, processor_class=CommandProcessor)
ContentProcessor.register(content_type=ContentType.History, processor_class=HistoryCommandProcessor)


#
#   Default Command Processor
#
class _DefaultCommandProcessor(CommandProcessor):

    #
    #   main
    #
    def process(self, content: Content, sender: ID, msg: InstantMessage) -> Content:
        if type(self) != _DefaultCommandProcessor:
            raise AssertionError('override me!')
        assert isinstance(content, Command), 'command error: %s' % content
        return TextContent.new(text='command (%s) not support yet!' % content.command)


# register
DefaultCommandName = 'default'
CommandProcessor.register(command=DefaultCommandName, processor_class=_DefaultCommandProcessor)
