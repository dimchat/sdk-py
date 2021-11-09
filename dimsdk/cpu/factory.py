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
    Processor Factory
    ~~~~~~~~~~~~~~~~~

    produce content/command processors
"""

import weakref
from typing import Dict, Optional, Union

from dimp import ContentType, Content, Command, GroupCommand

from .content import ContentProcessor
from .forward import ForwardContentProcessor

from .command import CommandProcessor
from .meta import MetaCommandProcessor
from .document import DocumentCommandProcessor

from .history import HistoryCommandProcessor, GroupCommandProcessor
from .grp_invite import InviteCommandProcessor
from .grp_expel import ExpelCommandProcessor
from .grp_quit import QuitCommandProcessor
from .grp_query import QueryCommandProcessor
from .grp_reset import ResetCommandProcessor


class ProcessorFactory:

    def __init__(self, messenger):
        super().__init__()
        self.__messenger = weakref.ref(messenger)
        self.__content_processors: Dict[int, ContentProcessor] = {}
        self.__command_processors: Dict[str, CommandProcessor] = {}

    @property
    def messenger(self):  # Messenger
        return self.__messenger()

    def get_processor(self, content: Content) -> Optional[ContentProcessor]:
        """
        Get content/command processor

        :param content: Content/Command
        :return: ContentProcessor
        """
        msg_type = content.type
        if isinstance(content, Command):
            name = content.command
            return self.get_command_processor(msg_type=msg_type, cmd_name=name)
        else:
            return self.get_content_processor(msg_type=msg_type)

    def get_content_processor(self, msg_type: Union[int, ContentType]) -> Optional[ContentProcessor]:
        if isinstance(msg_type, ContentType):
            msg_type = msg_type.value
        cpu = self.__content_processors.get(msg_type)
        if cpu is None:
            cpu = self._create_content_processor(msg_type=msg_type)
            if cpu is not None:
                self._put_content_processor(msg_type=msg_type, cpu=cpu)
        return cpu

    def get_command_processor(self, msg_type: Union[int, ContentType], cmd_name: str) -> Optional[CommandProcessor]:
        cpu = self._get_command_processor(cmd_name=cmd_name)
        if cpu is None:
            if isinstance(msg_type, ContentType):
                msg_type = msg_type.value
            cpu = self._create_command_processor(msg_type=msg_type, cmd_name=cmd_name)
            if cpu is not None:
                self._put_command_processor(cmd_name=cmd_name, cpu=cpu)
        return cpu

    # protected
    def _get_content_processor(self, msg_type: int) -> Optional[ContentProcessor]:
        return self.__content_processors.get(msg_type)

    # protected
    def _put_content_processor(self, msg_type: int, cpu: ContentProcessor):
        self.__content_processors[msg_type] = cpu

    # protected
    def _get_command_processor(self, cmd_name: str) -> Optional[CommandProcessor]:
        return self.__command_processors.get(cmd_name)

    # protected
    def _put_command_processor(self, cmd_name: str, cpu: CommandProcessor):
        self.__command_processors[cmd_name] = cpu

    # protected
    def _create_content_processor(self, msg_type: int) -> Optional[ContentProcessor]:
        """
        Create content processor with type

        :param msg_type: content type
        :return: ContentProcessor
        """
        # core contents
        if msg_type == ContentType.FORWARD.value:
            return ForwardContentProcessor(messenger=self.messenger)

    # protected
    def _create_command_processor(self, msg_type: int, cmd_name: str) -> Optional[CommandProcessor]:
        """
        Create command processor with name

        :param msg_type: content type
        :param cmd_name: command name
        :return: CommandProcessor
        """
        # meta
        if cmd_name == Command.META:
            return MetaCommandProcessor(messenger=self.messenger)
        # document
        if cmd_name == Command.DOCUMENT:
            return DocumentCommandProcessor(messenger=self.messenger)
        elif cmd_name in ['profile', 'visa', 'bulletin']:
            # share the same processor
            cpu = self._get_command_processor(cmd_name=Command.DOCUMENT)
            if cpu is None:
                cpu = DocumentCommandProcessor(messenger=self.messenger)
                self._put_command_processor(cmd_name=Command.DOCUMENT, cpu=cpu)
            return cpu
        # group
        if cmd_name == 'group':
            return GroupCommandProcessor(messenger=self.messenger)
        elif cmd_name == GroupCommand.INVITE:
            return InviteCommandProcessor(messenger=self.messenger)
        elif cmd_name == GroupCommand.EXPEL:
            return ExpelCommandProcessor(messenger=self.messenger)
        elif cmd_name == GroupCommand.QUIT:
            return QuitCommandProcessor(messenger=self.messenger)
        elif cmd_name == GroupCommand.QUERY:
            return QueryCommandProcessor(messenger=self.messenger)
        elif cmd_name == GroupCommand.RESET:
            return ResetCommandProcessor(messenger=self.messenger)
        # others
        if msg_type == ContentType.COMMAND.value:
            return CommandProcessor(messenger=self.messenger)
        elif msg_type == ContentType.HISTORY.value:
            return HistoryCommandProcessor(messenger=self.messenger)
