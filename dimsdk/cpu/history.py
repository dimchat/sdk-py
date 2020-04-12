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
    Group History Processors
    ~~~~~~~~~~~~~~~~~~~~~~~~

"""

from typing import Optional

from dimp import ID
from dimp import ReliableMessage
from dimp import ContentType, Content
from dimp import Command, GroupCommand

from .processor import ContentProcessor
from .command import CommandProcessor


class HistoryCommandProcessor(CommandProcessor):

    def __init__(self, messenger):
        super().__init__(messenger=messenger)
        # lazy
        self.__gpu: GroupCommandProcessor = None

    @property
    def gpu(self):  # GroupCommandProcessor
        if self.__gpu is None:
            self.__gpu = self._create_processor(GroupCommandProcessor)
        return self.__gpu

    #
    #   main
    #
    def process(self, content: Content, sender: ID, msg: ReliableMessage) -> Optional[Content]:
        assert type(self) == HistoryCommandProcessor, 'override me!'
        assert isinstance(content, Command), 'history cmd error: %s' % content
        if content.group is None:
            # get command processor
            cpu = self.cpu(command=content.command)
            # if cpu is None:
            #     return TextContent.new(text='History command (name: %s) not support yet!' % content.command)
        else:
            # get group command processor
            cpu = self.gpu
        assert cpu is not self, 'Dead cycle! history cmd: %s' % content
        return cpu.process(content=content, sender=sender, msg=msg)


class GroupCommandProcessor(HistoryCommandProcessor):

    def members(self, content: GroupCommand) -> Optional[list]:
        array = content.members
        if array is None:
            item = content.member
            if item is None:
                return None
            array = [item]
        return self.convert_members(array)

    def convert_members(self, array: list) -> list:
        facebook = self.facebook
        results = []
        for item in array:
            identifier = facebook.identifier(item)
            if identifier is None:
                raise ValueError('Member ID error: %s' % item)
            results.append(identifier)
        return results

    def contains_owner(self, members: list, group: ID) -> bool:
        facebook = self.facebook
        for item in members:
            user = facebook.identifier(item)
            if facebook.is_owner(member=user, group=group):
                return True

    def is_empty(self, group: ID) -> bool:
        """
        Check whether group info empty (lost)

        :param group: group ID
        :return: True on members, owner not found
        """
        facebook = self.facebook
        members = facebook.members(identifier=group)
        if members is None or len(members) == 0:
            return True
        owner = facebook.owner(identifier=group)
        if owner is None:
            return True

    #
    #   main
    #
    def process(self, content: Content, sender: ID, msg: ReliableMessage) -> Optional[Content]:
        assert type(self) == GroupCommandProcessor, 'override me!'
        assert isinstance(content, Command), 'group cmd error: %s' % content
        # process command by name
        cpu = self.cpu(command=content.command)
        # if cpu is None:
        #     return TextContent.new(text='Group command (name: %s) not support yet!' % content.command)
        assert cpu is not self, 'Dead cycle! group cmd: %s' % content
        return cpu.process(content=content, sender=sender, msg=msg)


# register
ContentProcessor.register(content_type=ContentType.History, processor_class=HistoryCommandProcessor)
