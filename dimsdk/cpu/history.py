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

from typing import List

from dimp import ID, ReliableMessage
from dimp import Content
from dimp import Command, GroupCommand

from .command import CommandProcessor


class HistoryCommandProcessor(CommandProcessor):

    FMT_HIS_CMD_NOT_SUPPORT = 'History command (name: %s) not support yet!'

    # Override
    def execute(self, cmd: Command, msg: ReliableMessage) -> List[Content]:
        text = self.FMT_HIS_CMD_NOT_SUPPORT % cmd.command
        return self._respond_text(text=text, group=cmd.group)


class GroupCommandProcessor(HistoryCommandProcessor):

    FMT_GRP_CMD_NOT_SUPPORT = 'Group command (name: %s) not support yet!'
    STR_GROUP_EMPTY = 'Group empty.'

    @staticmethod
    def members(cmd: GroupCommand) -> List[ID]:
        # get from 'members'
        array = cmd.members
        if array is None:
            # get from 'member
            item = cmd.member
            if item is None:
                array = []
            else:
                array = [item]
        return array

    # Override
    def execute(self, cmd: Command, msg: ReliableMessage) -> List[Content]:
        text = self.FMT_GRP_CMD_NOT_SUPPORT % cmd.command
        return self._respond_text(text=text, group=cmd.group)
