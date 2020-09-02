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
    Reset Group Command Processor
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    1. reset group members
    2. only group owner or assistant can reset group members

    3. specially, if the group members info lost,
       means you may not known who's the group owner immediately (and he may be not online),
       so we accept the new members-list temporary, and find out who is the owner,
       after that, we will send 'query' to the owner to get the newest members-list.
"""

from typing import Optional

from dimp import ID
from dimp import ReliableMessage
from dimp import Content
from dimp import GroupCommand

from .history import GroupCommandProcessor


class ResetCommandProcessor(GroupCommandProcessor):

    def __temporary(self, sender: ID, members: list, group: ID) -> Optional[Content]:
        if self.contains_owner(members=members, group=group):
            facebook = self.facebook
            # temporary save
            if facebook.save_members(members=members, identifier=group):
                owner = facebook.owner(identifier=group)
                if owner is not None and owner != sender:
                    # NOTICE: to prevent counterfeit,
                    #         query the owner for newest member-list
                    cmd = GroupCommand.query(group=group)
                    self.messenger.send_content(content=cmd, receiver=owner)
            # response (no need to response this group command)
            return None
        else:
            # NOTICE: this is a partial member-list
            #         query the sender for full-list
            return GroupCommand.query(group=group)

    def __reset(self, new_members: list, group: ID) -> (list, list):
        facebook = self.facebook
        # existed members
        members: list = facebook.members(identifier=group)
        if members is None:
            members = []
        # removed member(s)
        remove_list = []
        for item in members:
            if item not in new_members:
                # found
                remove_list.append(item)
        # added member(s)
        add_list = []
        for item in new_members:
            if item not in members:
                # found
                add_list.append(item)
        # save changes
        if len(add_list) > 0 or len(remove_list) > 0:
            if not facebook.save_members(members=new_members, identifier=group):
                return None, None
        return add_list, remove_list

    #
    #   main
    #
    def process(self, content: Content, sender: ID, msg: ReliableMessage) -> Optional[Content]:
        # assert isinstance(content, ResetCommand), 'group command error: %s' % content
        assert isinstance(content, GroupCommand), 'group command error: %s' % content
        facebook = self.facebook
        # new members
        new_members: list = self.members(content=content)
        if new_members is None or len(new_members) == 0:
            raise ValueError('reset group command error: %s' % content)
        group: ID = content.group
        # 0. check whether group info empty
        if self.is_empty(group=group):
            # FIXME: group profile lost?
            # FIXME: how to avoid strangers impersonating group members?
            return self.__temporary(sender=sender, members=new_members, group=group)
        # 1. check permission
        if not facebook.is_owner(member=sender, group=group):
            if not facebook.exists_assistant(member=sender, group=group):
                raise AssertionError('only owner/assistant can reset: %s, %s' % (group, sender))
        # 2. reset
        added, removed = self.__reset(new_members=new_members, group=group)
        if added is not None:
            content['added'] = added
        if removed is not None:
            content['removed'] = removed
        # 3. response (no need to response this group command)
        return None


# register
GroupCommandProcessor.register(command=GroupCommand.RESET, processor_class=ResetCommandProcessor)
