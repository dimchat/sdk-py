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

from typing import Optional

from dimp import ID
from dimp import ReliableMessage
from dimp import Content
from dimp import GroupCommand, InviteCommand

from .history import GroupCommandProcessor


class InviteCommandProcessor(GroupCommandProcessor):

    def __is_reset(self, sender: ID, group: ID, invite_list: list) -> bool:
        """
        Check whether this is a 'reset' command

        :param sender:      owner ID?
        :param group:       group ID
        :param invite_list: new members list
        :return: True on owner invites owner
        """
        if self.contains_owner(members=invite_list, group=group):
            # NOTICE: owner invite owner?
            #         it's a Reset command!
            if self.facebook.is_owner(member=sender, group=group):
                return True

    def __reset(self, content: Content, sender: ID, msg: ReliableMessage) -> Content:
        """
        Call reset command processor

        :param content: invite(reset) command
        :param sender:  owner ID?
        :param msg:     instant message
        :return: response from invite command processor
        """
        cpu: GroupCommandProcessor = self.cpu(command=GroupCommand.RESET)
        assert cpu is not None, 'failed to get "reset" command processor'
        return cpu.process(content=content, sender=sender, msg=msg)

    def __add(self, invite_list: list, group: ID) -> Optional[list]:
        facebook = self.facebook
        # existed members
        members: list = facebook.members(identifier=group)
        if members is None:
            members = []
        # added member(s)
        add_list = []
        for item in invite_list:
            if item in members:
                continue
            # new member found
            add_list.append(item)
            members.append(item)
        # response added-list after changed
        if len(add_list) > 0:
            if facebook.save_members(members=members, identifier=group):
                return add_list

    #
    #   main
    #
    def process(self, content: Content, sender: ID, msg: ReliableMessage) -> Optional[Content]:
        assert isinstance(content, InviteCommand), 'group command error: %s' % content
        facebook = self.facebook
        group: ID = content.group
        # 0. check whether group info empty
        if self.is_empty(group=group):
            # NOTICE:
            #     group membership lost?
            #     reset group members
            return self.__reset(content=content, sender=sender, msg=msg)
        # 1. check permission
        if not facebook.exists_member(member=sender, group=group):
            if not facebook.exists_assistant(member=sender, group=group):
                if not facebook.is_owner(member=sender, group=group):
                    raise AssertionError('only member/assistant can invite: %s' % msg)
        # 2. get inviting members
        invite_list: list = self.members(content=content)
        if invite_list is None or len(invite_list) == 0:
            raise ValueError('invite command error: %s' % content)
        # 2.1. check founder for reset command
        if self.__is_reset(sender=sender, group=group, invite_list=invite_list):
            # NOTICE:
            #     owner invites owner?
            #     it means this should be a 'reset' command
            return self.__reset(content=content, sender=sender, msg=msg)
        # 2.2. get invited-list
        add_list = self.__add(invite_list=invite_list, group=group)
        if add_list is not None:
            content['added'] = add_list
        # 3. response (no need to response this group command)
        return None


# register
GroupCommandProcessor.register(command=GroupCommand.INVITE, processor_class=InviteCommandProcessor)
