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
from typing import Optional, List

from dimp import ReliableMessage
from dimp import Content


# -----------------------------------------------------------------------------
#  ContentProcessor (CPU: Content Processing Unit)
# -----------------------------------------------------------------------------

class ContentProcessor(ABC):
    """Content processing unit (CPU) - core interface for handling message content.

    Defines the standard interface for processing different types of message content
    (e.g., text, commands, files, ...) and generating response content.

    Each implementation handles a specific content type or command, following the
    single responsibility principle.
    """

    @abstractmethod
    async def process_content(self, content: Content, r_msg: ReliableMessage) -> List[Content]:
        """Processes incoming message content and generates response contents.

        :param content: incoming message content to process (e.g., text, command, file, ...)
        :param r_msg:   original reliable message (provides context: sender, receiver, envelope)
        :return: list of response content items (empty list if no response is needed)
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.process_content()'
        )


# -----------------------------------------------------------------------------
#  ContentProcessorCreator (CPU Creator)
# -----------------------------------------------------------------------------

class ContentProcessorCreator(ABC):
    """Creator interface for instantiating content/command processors.

    Implements the Factory Method pattern to create specific
    :class:`ContentProcessor` instances based on content type or command name,
    decoupling creation logic from usage logic.
    """

    @abstractmethod
    def create_content_processor(self, msg_type: str) -> Optional[ContentProcessor]:
        """Creates a content processor for a specific content type.

        :param msg_type: content type identifier (e.g., "text", "command", "file", ...)
        :return: specific :class:`ContentProcessor` instance (null if type is unsupported)
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.create_content_processor()'
        )

    @abstractmethod
    def create_command_processor(self, msg_type: str, cmd: str) -> Optional[ContentProcessor]:
        """Creates a command processor for a specific content type and command name.

        :param msg_type: content type identifier (typically "command" for command content)
        :param cmd:      command name (e.g., "meta", "documents", "group", ...)
        :return: specific command processor instance (null if command is unsupported)
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.create_command_processor()'
        )


# -----------------------------------------------------------------------------
#  ContentProcessorFactory (CPU Factory)
# -----------------------------------------------------------------------------

class ContentProcessorFactory(ABC):
    """Factory interface for retrieving cached content/command processors.

    Manages a cache of :class:`ContentProcessor` instances to avoid repeated creation,
    and provides unified access to processors for different content types/commands.
    """

    @abstractmethod
    def get_content_processor(self, content: Content) -> Optional[ContentProcessor]:
        """Retrieves the appropriate processor for a given content instance.

        For command content:
        1. First tries to get a processor for the specific command name
        2. Falls back to group command processor (if applicable)
        3. Finally uses the default content processor for the content type

        :param content: content instance to get processor for (can be regular content or command)
        :return: matching :class:`ContentProcessor` instance (null if no processor found)
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.get_content_processor()'
        )

    @abstractmethod
    def get_content_processor_for_type(self, msg_type: str) -> Optional[ContentProcessor]:
        """Retrieves a content processor for a specific content type.

        :param msg_type: content type identifier (e.g., "text", "command", "file", ...)
        :return: :class:`ContentProcessor` instance for the type (null if type is unsupported)
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.get_content_processor_for_type()'
        )
