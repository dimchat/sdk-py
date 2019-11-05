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
    Quit Group Command Processor
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    1. quit the group
    2. owner and assistant cannot quit
    3. assistant can be hired/fired by owner
"""

from dimp import ID
from dimp import InstantMessage
from dimp import Content
from dimp import GroupCommand, QuitCommand

from .group import GroupCommandProcessor


class QuitCommandProcessor(GroupCommandProcessor):

    #
    #   main
    #
    def process(self, content: Content, sender: ID, msg: InstantMessage) -> bool:
        if type(self) != QuitCommandProcessor:
            raise AssertionError('override me!')
        assert isinstance(content, QuitCommand), 'group command error: %s' % content
        group: ID = self.facebook.identifier(content.group)
        # 1. check permission
        if self.is_owner(member=sender, group=group):
            self.error('owner cannot quit: %s' % msg)
            return False
        if self.exists_assistant(member=sender, group=group):
            self.error('assistant cannot quit: %s' % msg)
            return False
        if not self.exists_member(member=sender, group=group):
            self.error('not a member yet: %s' % msg)
            return False
        # 2. remove sender from group members
        members: list = self.facebook.members(identifier=group)
        if members is None:
            raise AssertionError('members error: %s' % group)
        assert sender in members, 'quit command error: %s' % msg
        members.remove(sender)
        # 3. save
        return self.facebook.save_members(members=members, identifier=group)


# register
GroupCommandProcessor.register(command=GroupCommand.QUIT, processor_class=QuitCommandProcessor)
