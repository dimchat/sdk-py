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
    Group Command Processor
    ~~~~~~~~~~~~~~~~~~~~~~~

"""

from typing import Optional

from dimp import NetworkID, ID
from dimp import InstantMessage
from dimp import Content
from dimp import Command, GroupCommand

from .command import CommandProcessor, HistoryCommandProcessor


class GroupCommandProcessor(HistoryCommandProcessor):

    def id_list(self, array: list) -> list:
        results = []
        for item in array:
            results.append(self.facebook.identifier(item))
        return results

    def is_founder(self, member: ID, group: ID) -> bool:
        founder = self.facebook.founder(identifier=group)
        if founder is not None:
            return founder == member
        g_meta = self.facebook.meta(identifier=group)
        if g_meta is not None:
            meta = self.facebook.meta(identifier=member)
            if meta is not None:
                return g_meta.match_public_key(meta.key)

    def is_owner(self, member: ID, group: ID) -> bool:
        if group.type == NetworkID.Polylogue:
            return self.is_founder(member=member, group=group)

    def contains_owner(self, members: list, group: ID) -> bool:
        for item in members:
            user = self.facebook.identifier(item)
            if self.is_owner(member=user, group=group):
                return True

    def exists_member(self, member: ID, group: ID) -> bool:
        owner = self.facebook.owner(identifier=group)
        if owner is not None and owner == member:
            return True
        members = self.facebook.members(identifier=group)
        if members is not None:
            return member in members

    def exists_assistant(self, member: ID, group: ID) -> bool:
        assistants = self.facebook.assistants(identifier=group)
        if assistants is not None:
            return member in assistants

    def members(self, content: GroupCommand) -> Optional[list]:
        array = content.members
        if array is not None:
            return self.id_list(array=array)
        member = content.member
        if member is not None:
            member = self.facebook.identifier(member)
            return [member]

    #
    #   main
    #
    def process(self, content: Content, sender: ID, msg: InstantMessage) -> Content:
        if type(self) != GroupCommandProcessor:
            raise AssertionError('override me!')
        assert isinstance(content, Command), 'group command error: %s' % content
        # process command by name
        cpu: CommandProcessor = self.cpu(command=content.command)
        assert cpu is not self, 'Dead cycle! group command: %s' % content
        return cpu.process(content=content, sender=sender, msg=msg)
