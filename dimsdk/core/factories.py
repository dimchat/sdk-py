# -*- coding: utf-8 -*-
#
#   DIMP : Decentralized Instant Messaging Protocol
#
#                                Written in 2022 by Moky <albert.moky@gmail.com>
#
# ==============================================================================
# MIT License
#
# Copyright (c) 2022 Albert Moky
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

from typing import Optional, Any, Dict

from dimp import Envelope, InstantMessage, SecureMessage, ReliableMessage
from dimp import ContentType, Content
from dimp import Command, GroupCommand
from dimp.protocol import CommandFactory
from dimp.dkd import ContentFactory
from dimp.dkd import CommandFactoryManager
from dimp.dkd import BaseContent
from dimp.dkd import BaseTextContent, ListContent, SecretContent
from dimp.dkd import WebPageContent, NameCardContent
from dimp.dkd import BaseFileContent, ImageFileContent, AudioFileContent, VideoFileContent
from dimp.dkd import BaseMoneyContent, TransferMoneyContent
from dimp.dkd import AppCustomizedContent
from dimp.dkd import BaseCommand
from dimp.dkd import BaseMetaCommand, BaseDocumentCommand
from dimp.dkd import BaseReceiptCommand
from dimp.dkd import BaseHistoryCommand, BaseGroupCommand
from dimp.dkd import InviteGroupCommand, ExpelGroupCommand, JoinGroupCommand
from dimp.dkd import QuitGroupCommand, QueryGroupCommand, ResetGroupCommand
from dimp.dkd import HireGroupCommand, FireGroupCommand, ResignGroupCommand

from ..msg import MessageFactory


class ContentFactoryBuilder(ContentFactory):

    def __init__(self, content_class):
        super().__init__()
        self.__class = content_class

    # Override
    def parse_content(self, content: Dict[str, Any]) -> Optional[Content]:
        # return self.__class(content=content)
        return self.__class(content)


class CommandFactoryBuilder(CommandFactory):

    def __init__(self, command_class):
        super().__init__()
        self.__class = command_class

    # Override
    def parse_command(self, content: Dict[str, Any]) -> Optional[Command]:
        # return self.__class(content=content)
        return self.__class(content)


#
#   General Command Factory
#   ~~~~~~~~~~~~~~~~~~~~~~~
#
class GeneralCommandFactory(ContentFactory, CommandFactory):

    def __init__(self):
        super().__init__()

    # Override
    def parse_content(self, content: Dict[str, Any]) -> Optional[Content]:
        gf = CommandFactoryManager.general_factory
        # get factory by command name
        name = gf.get_cmd(content=content, default='*')
        factory = gf.get_command_factory(cmd=name)
        if factory is None:
            # check for group command
            if 'group' in content:  # and name != 'group':
                factory = gf.get_command_factory(cmd='group')
            if factory is None:
                factory = self
        return factory.parse_command(content=content)

    # Override
    def parse_command(self, content: Dict[str, Any]) -> Optional[Command]:
        return BaseCommand(content=content)


class HistoryCommandFactory(GeneralCommandFactory):

    # Override
    def parse_command(self, content: Dict[str, Any]) -> Optional[Command]:
        return BaseHistoryCommand(content=content)


class GroupCommandFactory(HistoryCommandFactory):

    # Override
    def parse_content(self, content: Dict[str, Any]) -> Optional[Content]:
        gf = CommandFactoryManager.general_factory
        # get factory by command name
        name = gf.get_cmd(content=content, default='*')
        factory = gf.get_command_factory(cmd=name)
        if factory is None:
            factory = self
        return factory.parse_command(content=content)

    # Override
    def parse_command(self, content: Dict[str, Any]) -> Optional[Command]:
        return BaseGroupCommand(content=content)


def register_message_factories():
    """ Register core message factories """
    factory = MessageFactory()
    # Envelope factory
    Envelope.register(factory=factory)
    # Message factories
    InstantMessage.register(factory=factory)
    SecureMessage.register(factory=factory)
    ReliableMessage.register(factory=factory)


def register_content_factories():
    """ Register core content factories """
    # Text
    Content.register(msg_type=ContentType.TEXT, factory=ContentFactoryBuilder(content_class=BaseTextContent))

    # File
    Content.register(msg_type=ContentType.FILE, factory=ContentFactoryBuilder(content_class=BaseFileContent))
    # Image
    Content.register(msg_type=ContentType.IMAGE, factory=ContentFactoryBuilder(content_class=ImageFileContent))
    # Audio
    Content.register(msg_type=ContentType.AUDIO, factory=ContentFactoryBuilder(content_class=AudioFileContent))
    # Video
    Content.register(msg_type=ContentType.VIDEO, factory=ContentFactoryBuilder(content_class=VideoFileContent))

    # Web Page
    Content.register(msg_type=ContentType.PAGE, factory=ContentFactoryBuilder(content_class=WebPageContent))

    # Name Card
    Content.register(msg_type=ContentType.NAME_CARD, factory=ContentFactoryBuilder(content_class=NameCardContent))

    # Money
    Content.register(msg_type=ContentType.MONEY, factory=ContentFactoryBuilder(content_class=BaseMoneyContent))
    Content.register(msg_type=ContentType.TRANSFER, factory=ContentFactoryBuilder(content_class=TransferMoneyContent))
    # ...

    # Command
    Content.register(msg_type=ContentType.COMMAND, factory=GeneralCommandFactory())

    # History Command
    Content.register(msg_type=ContentType.HISTORY, factory=HistoryCommandFactory())

    # # Application Customized
    # Content.register(msg_type=ContentType.APPLICATION,
    #                  factory=ContentFactoryBuilder(content_class=AppCustomizedContent))
    # Content.register(msg_type=ContentType.CUSTOMIZED,
    #                  factory=ContentFactoryBuilder(content_class=AppCustomizedContent))

    # Content Array
    Content.register(msg_type=ContentType.ARRAY, factory=ContentFactoryBuilder(content_class=ListContent))

    # Top-Secret
    Content.register(msg_type=ContentType.FORWARD, factory=ContentFactoryBuilder(content_class=SecretContent))

    # Unknown Content Type
    Content.register(msg_type=0, factory=ContentFactoryBuilder(content_class=BaseContent))


def register_command_factories():
    """ Register core command factories """
    # Meta Command
    Command.register(cmd=Command.META, factory=CommandFactoryBuilder(command_class=BaseMetaCommand))

    # Document Command
    Command.register(cmd=Command.DOCUMENT, factory=CommandFactoryBuilder(command_class=BaseDocumentCommand))

    # Receipt Command
    Command.register(cmd=Command.RECEIPT, factory=CommandFactoryBuilder(command_class=BaseReceiptCommand))

    # Group Commands
    Command.register(cmd='group', factory=GroupCommandFactory())
    Command.register(cmd=GroupCommand.INVITE, factory=CommandFactoryBuilder(command_class=InviteGroupCommand))
    # 'expel' is deprecated (use 'reset' instead)
    Command.register(cmd=GroupCommand.EXPEL, factory=CommandFactoryBuilder(command_class=ExpelGroupCommand))
    Command.register(cmd=GroupCommand.JOIN, factory=CommandFactoryBuilder(command_class=JoinGroupCommand))
    Command.register(cmd=GroupCommand.QUIT, factory=CommandFactoryBuilder(command_class=QuitGroupCommand))
    Command.register(cmd=GroupCommand.QUERY, factory=CommandFactoryBuilder(command_class=QueryGroupCommand))
    Command.register(cmd=GroupCommand.RESET, factory=CommandFactoryBuilder(command_class=ResetGroupCommand))
    # Group Admin Commands
    Command.register(cmd=GroupCommand.HIRE, factory=CommandFactoryBuilder(command_class=HireGroupCommand))
    Command.register(cmd=GroupCommand.FIRE, factory=CommandFactoryBuilder(command_class=FireGroupCommand))
    Command.register(cmd=GroupCommand.RESIGN, factory=CommandFactoryBuilder(command_class=ResignGroupCommand))


def register_all_factories():
    """ Register All Message/Content/Command Factories """
    # register core factories
    register_message_factories()
    register_content_factories()
    register_command_factories()
    # register customized factories
    factory = ContentFactoryBuilder(content_class=AppCustomizedContent)
    Content.register(msg_type=ContentType.APPLICATION, factory=factory)
    Content.register(msg_type=ContentType.CUSTOMIZED, factory=factory)
