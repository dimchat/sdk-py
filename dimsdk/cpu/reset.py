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

from dimp import ID
from dimp import InstantMessage
from dimp import Content
from dimp import GroupCommand, ResetCommand

from .group import GroupCommandProcessor


class ResetCommandProcessor(GroupCommandProcessor):

    def __query(self, group: ID, receiver: ID) -> bool:
        cmd = GroupCommand.query(group=group)
        return self.messenger.send_content(content=cmd, receiver=receiver)

    #
    #   main
    #
    def process(self, content: Content, sender: ID, msg: InstantMessage) -> bool:
        if type(self) != ResetCommandProcessor:
            raise AssertionError('override me!')
        assert isinstance(content, ResetCommand), 'group command error: %s' % content
        # new members
        new_members: list = self.members(content=content)
        if new_members is None or len(new_members) == 0:
            self.error('reset group command error: %s' % content)
            return False
        # existed members
        group: ID = self.facebook.identifier(content.group)
        members: list = self.facebook.members(identifier=group)
        if members is None:
            members = []
        # 1. check permission
        founder: ID = self.facebook.founder(identifier=group)
        if founder is None and len(members) == 0:
            # FIXME: group profile lost?
            # FIXME: how to avoid strangers impersonating group members?
            if not self.contains_owner(members=new_members, group=group):
                self.error('owner not found, reject this command: %s' % content)
                # query the sender to reset with full member-list
                return self.__query(group=group, receiver=sender)
            # now this new member-list contains the group owner
            # TODO: if the sender is not owner, query the owner for newest member list
        elif not self.is_owner(member=sender, group=group):
            if not self.exists_assistant(member=sender, group=group):
                self.error('only owner/assistant can reset: %s' % msg)
                return False
        # 2.1. check removed member(s)
        remove_list = []
        for item in members:
            if item in new_members:
                continue
            remove_list.append(item)
        # 2.2. check added member(s)
        add_list = []
        for item in new_members:
            if item in members:
                continue
            # new member found
            add_list.append(item)
        # 3. save
        if len(add_list) > 0:
            content['added'] = add_list
        if len(remove_list) > 0:
            content['removed'] = remove_list
        if len(add_list) > 0 or len(remove_list) > 0:
            return self.facebook.save_members(members=new_members, identifier=group)
        else:
            # nothing changed
            return True


# register
GroupCommandProcessor.register(command=GroupCommand.RESET, processor_class=ResetCommandProcessor)
