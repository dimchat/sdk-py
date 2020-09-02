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

from typing import Optional

from dimp import ID
from dimp import ReliableMessage
from dimp import Content
from dimp import GroupCommand, QuitCommand

from .history import GroupCommandProcessor


class QuitCommandProcessor(GroupCommandProcessor):

    def __remove(self, sender: ID, group: ID) -> bool:
        facebook = self.facebook
        members = facebook.members(identifier=group)
        if members is None:
            return False
        if sender not in members:
            return False
        members.remove(sender)
        return facebook.save_members(members=members, identifier=group)

    #
    #   main
    #
    def process(self, content: Content, sender: ID, msg: ReliableMessage) -> Optional[Content]:
        assert isinstance(content, QuitCommand), 'group command error: %s' % content
        facebook = self.facebook
        group: ID = content.group
        # 1. check permission
        if facebook.is_owner(member=sender, group=group):
            raise AssertionError('owner cannot quit: %s' % msg)
        if facebook.exists_assistant(member=sender, group=group):
            raise AssertionError('assistant cannot quit: %s' % msg)
        # 2. remove sender from group members
        self.__remove(sender=sender, group=group)
        # 3. response (no need to response this group command)
        return None


# register
GroupCommandProcessor.register(command=GroupCommand.QUIT, processor_class=QuitCommandProcessor)
