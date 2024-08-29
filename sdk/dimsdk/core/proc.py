# -*- coding: utf-8 -*-
#
#   DIM-SDK : Decentralized Instant Messaging Software Development Kit
#
#                                Written in 2021 by Moky <albert.moky@gmail.com>
#
# ==============================================================================
# MIT License
#
# Copyright (c) 2021 Albert Moky
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

from abc import ABC, abstractmethod
from typing import Optional, List, Dict

from dimp import ReliableMessage
from dimp import Content, Command, GroupCommand

from .twins import TwinsHelper


class ContentProcessor(ABC):
    """
        CPU: Content Processing Unit
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    @abstractmethod
    async def process_content(self, content: Content, r_msg: ReliableMessage) -> List[Content]:
        """
        Process message content

        :param content: content received
        :param r_msg:   reliable message
        :return: responses to sender
        """
        raise NotImplemented


class ContentProcessorCreator(ABC):
    """
        CPU Creator
        ~~~~~~~~~~~

        Delegate for CPU Factory
    """

    @abstractmethod
    def create_content_processor(self, msg_type: int) -> Optional[ContentProcessor]:
        """
        Create content processor with type

        :param msg_type: content type
        :return ContentProcessor
        """
        raise NotImplemented

    @abstractmethod
    def create_command_processor(self, msg_type: int, cmd: str) -> Optional[ContentProcessor]:
        """
        Create command processor with name

        :param msg_type: content type
        :param cmd:      command name
        :return CommandProcessor
        """
        raise NotImplemented


class ContentProcessorFactory(ABC):
    """
        CPU Factory
        ~~~~~~~~~~~

        Delegate for Message Processor
    """

    @abstractmethod
    def get_processor(self, content: Content) -> Optional[ContentProcessor]:
        """
        Get content/command processor

        :param content: Content/Command
        :return: ContentProcessor
        """
        raise NotImplemented

    @abstractmethod
    def get_content_processor(self, msg_type: int) -> Optional[ContentProcessor]:
        raise NotImplemented

    @abstractmethod
    def get_command_processor(self, msg_type: int, cmd: str) -> Optional[ContentProcessor]:
        raise NotImplemented


class GeneralContentProcessorFactory(TwinsHelper, ContentProcessorFactory):
    """ General ContentProcessor Factory """

    def __init__(self, facebook, messenger, creator: ContentProcessorCreator):
        super().__init__(facebook=facebook, messenger=messenger)
        self.__creator = creator
        self.__content_processors: Dict[int, ContentProcessor] = {}
        self.__command_processors: Dict[str, ContentProcessor] = {}

    @property  # protected
    def creator(self) -> ContentProcessorCreator:
        return self.__creator

    # protected
    def _get_content_processor(self, msg_type: int) -> Optional[ContentProcessor]:
        return self.__content_processors.get(msg_type)

    # protected
    def _put_content_processor(self, msg_type: int, cpu: ContentProcessor):
        self.__content_processors[msg_type] = cpu

    # protected
    def _get_command_processor(self, cmd: str) -> Optional[ContentProcessor]:
        return self.__command_processors.get(cmd)

    # protected
    def _put_command_processor(self, cmd: str, cpu: ContentProcessor):
        self.__command_processors[cmd] = cpu

    #
    #   ContentProcessorFactory
    #

    # Override
    def get_processor(self, content: Content) -> Optional[ContentProcessor]:
        msg_type = content.type
        if isinstance(content, Command):
            name = content.cmd
            # command processor
            cpu = self.get_command_processor(msg_type, cmd=name)
            if cpu is not None:
                return cpu
            elif isinstance(content, GroupCommand):
                # group command processor
                cpu = self.get_command_processor(msg_type, cmd='group')
                if cpu is not None:
                    return cpu
        # content processor
        return self.get_content_processor(msg_type)

    # Override
    def get_content_processor(self, msg_type: int) -> Optional[ContentProcessor]:
        cpu = self._get_content_processor(msg_type)
        if cpu is None:
            cpu = self.creator.create_content_processor(msg_type)
            if cpu is not None:
                self._put_content_processor(msg_type, cpu=cpu)
        return cpu

    # Override
    def get_command_processor(self, msg_type: int, cmd: str) -> Optional[ContentProcessor]:
        cpu = self._get_command_processor(cmd=cmd)
        if cpu is None:
            cpu = self.creator.create_command_processor(msg_type, cmd=cmd)
            if cpu is not None:
                self._put_command_processor(cmd=cmd, cpu=cpu)
        return cpu
