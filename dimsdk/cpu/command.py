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

from dimp import Envelope, Content, Command, HistoryCommand

from .processor import ContentProcessor


class CommandProcessor(ContentProcessor):

    def __init__(self, messenger):
        super().__init__(messenger)
        # command processing units
        self.__processors = {}

    def cpu(self, command: str):
        cpu = self.__processors.get(command)
        if cpu is not None:
            return cpu
        # try to create new processor
        clazz = self.processor_class(command=command)
        if clazz is not None:
            cpu = clazz(self.messenger)
            self.__processors[command] = cpu
            return cpu

    def process(self, content: Content, envelope: Envelope) -> bool:
        if type(self) != CommandProcessor:
            raise AssertionError('override me!')
        assert isinstance(content, Command)
        # process command by name
        cpu: CommandProcessor = self.cpu(command=content.command)
        if cpu is None:
            self.error('command (%s) not support yet!' % content.command)
            return False
        if cpu is self:
            raise AssertionError('Dead cycle! command: %s' % content)
        try:
            # process by subclass
            return cpu.process(content=content, envelope=envelope)
        except Exception as error:
            self.error('command error: %s' % error)
            return False

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
    def processor_class(cls, command: str):
        return cls.__command_processor_classes.get(command)


class HistoryCommandProcessor(CommandProcessor):

    def __init__(self, messenger):
        super().__init__(messenger)
        # command processing units
        from .group import GroupCommandProcessor
        self.__gpu = GroupCommandProcessor(self.messenger)

    def process(self, content: Content, envelope: Envelope) -> bool:
        if type(self) != HistoryCommandProcessor:
            raise AssertionError('override me!')
        assert isinstance(content, HistoryCommand)
        if content.group is not None:
            # group command
            return self.__gpu.process(content=content, envelope=envelope)
        # process command by name
        cpu: CommandProcessor = self.cpu(command=content.command)
        if cpu is not None:
            return cpu.process(content=content, envelope=envelope)
