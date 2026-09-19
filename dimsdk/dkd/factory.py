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

from typing import Optional

from dimp import Content, Command

from .proc import ContentProcessor
from .proc import ContentProcessorCreator
from .proc import ContentProcessorFactory


"""
    Generic for CPU
    ~~~~~~~~~~~~~~~
"""
try:
    import collections.abc as abc
    CpuMap = abc.MutableMapping[str, ContentProcessor]
except TypeError:
    import typing
    CpuMap = typing.MutableMapping[str, ContentProcessor]


# -----------------------------------------------------------------------------
#  GeneralContentProcessorFactory (Concrete CPU Factory)
# -----------------------------------------------------------------------------

class GeneralContentProcessorFactory(ContentProcessorFactory):
    """General implementation of :class:`ContentProcessorFactory` with caching support.

    Maintains caches for content processors and command processors to reuse instances,
    delegating creation to a :class:`ContentProcessorCreator` when cache misses occur.
    """

    def __init__(self, creator: ContentProcessorCreator):
        super().__init__()
        self.__creator = creator
        # Cache of content processors (key: content type).
        self.__content_processors: CpuMap = {}
        # Cache of command processors (key: command name).
        self.__command_processors: CpuMap = {}

    @property  # protected
    def creator(self) -> ContentProcessorCreator:
        return self.__creator

    #
    #   ContentProcessorFactory
    #

    # Override
    def get_content_processor(self, content: Content) -> Optional[ContentProcessor]:
        msg_type = content.type
        if isinstance(content, Command):
            name = content.cmd
            cpu = self._get_command_processor(msg_type, cmd=name)
            if cpu is not None:
                return cpu
            # TODO: check for group command
        # content processor
        return self.get_content_processor_for_type(msg_type)

    # Override
    def get_content_processor_for_type(self, msg_type: str) -> Optional[ContentProcessor]:
        cpu = self.__content_processors.get(msg_type)
        if cpu is None:
            cpu = self.creator.create_content_processor(msg_type)
            if cpu is not None:
                self.__content_processors[msg_type] = cpu
        return cpu

    # private
    def _get_command_processor(self, msg_type: str, cmd: str) -> Optional[ContentProcessor]:
        """Retrieves a command processor from cache (or creates it).

        Private helper method - internal use only.

        `msg_type` is the content type identifier (typically "command").
        `cmd` is the command name (e.g., "meta", "documents", "group", ...).

        Returns the command processor instance (null if unsupported).
        """
        cpu = self.__command_processors.get(cmd)
        if cpu is None:
            cpu = self.creator.create_command_processor(msg_type, cmd=cmd)
            if cpu is not None:
                self.__command_processors[cmd] = cpu
        return cpu
