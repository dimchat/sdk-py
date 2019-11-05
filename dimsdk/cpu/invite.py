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
    Invite Group Command Processor
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    1. add new member(s) to the group
    2. any member or assistant can invite new member
"""

from dimp import ID
from dimp import InstantMessage
from dimp import Content
from dimp import GroupCommand, InviteCommand

from .command import CommandProcessor
from .group import GroupCommandProcessor


class InviteCommandProcessor(GroupCommandProcessor):

    def __reset(self, content: Content, sender: ID, msg: InstantMessage) -> bool:
        cpu: CommandProcessor = self.cpu(command=GroupCommand.RESET)
        assert cpu is not None, 'failed to get "invite" command processor'
        return cpu.process(content=content, sender=sender, msg=msg)

    #
    #   main
    #
    def process(self, content: Content, sender: ID, msg: InstantMessage) -> bool:
        if type(self) != InviteCommandProcessor:
            raise AssertionError('override me!')
        assert isinstance(content, InviteCommand), 'group command error: %s' % content
        # inviting members
        invite_list: list = self.members(content=content)
        if invite_list is None or len(invite_list) == 0:
            self.error('invite command error: %s' % content)
            return False
        # existed members
        group: ID = self.facebook.identifier(content.group)
        members: list = self.facebook.members(identifier=group)
        if members is None:
            members = []
        # 1. check permission
        founder: ID = self.facebook.founder(identifier=group)
        if founder is None and len(members) == 0:
            # NOTICE:
            #     group profile lost?
            #     reset group members
            return self.__reset(content=content, sender=sender, msg=msg)
        if not self.exists_member(member=sender, group=group):
            if not self.exists_assistant(member=sender, group=group):
                self.error('only member/assistant can invite: %s' % msg)
                return False
        # 1.1. check founder for reset command
        if self.is_owner(member=sender, group=group):
            if self.contains_owner(members=invite_list, group=group):
                # NOTICE:
                #     owner invites owner?
                #     it means this should be a 'reset' command
                return self.__reset(content=content, sender=sender, msg=msg)
        # 2. check added member(s)
        add_list = []
        for item in invite_list:
            if item in members:
                continue
            # new member found
            add_list.append(item)
            members.append(item)
        # 3. save
        if len(add_list) > 0:
            content['added'] = add_list
            return self.facebook.save_members(members=members, identifier=group)
        else:
            # nothing changed
            return True


# register
GroupCommandProcessor.register(command=GroupCommand.INVITE, processor_class=InviteCommandProcessor)
