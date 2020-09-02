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
    Expel Group Command Processor
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    1. remove group member(s)
    2. only group owner or assistant can expel member
"""

from typing import Optional

from dimp import ID
from dimp import ReliableMessage
from dimp import Content
from dimp import GroupCommand, ExpelCommand

from .history import GroupCommandProcessor


class ExpelCommandProcessor(GroupCommandProcessor):

    def __remove(self, expel_list: list, group: ID) -> Optional[list]:
        facebook = self.facebook
        # existed members
        members: list = facebook.members(identifier=group)
        if members is None:
            members = []
        # removed member(s)
        remove_list = []
        for item in expel_list:
            if item not in members:
                continue
            # expelled member found
            remove_list.append(item)
            members.remove(item)
        # response removed-list after changed
        if len(remove_list) > 0:
            if facebook.save_members(members=members, identifier=group):
                return remove_list

    #
    #   main
    #
    def process(self, content: Content, sender: ID, msg: ReliableMessage) -> Optional[Content]:
        assert isinstance(content, ExpelCommand), 'group command error: %s' % content
        facebook = self.facebook
        group: ID = content.group
        # 1. check permission
        if not facebook.is_owner(member=sender, group=group):
            if not facebook.exists_assistant(member=sender, group=group):
                raise AssertionError('only owner/assistant can expel: %s' % msg)
        # 2.1. get expelling members
        expel_list: list = self.members(content=content)
        if expel_list is None or len(expel_list) == 0:
            raise ValueError('expel command error: %s' % content)
        # 2.2. get removed-list
        remove_list = self.__remove(expel_list=expel_list, group=group)
        if remove_list is not None:
            content['removed'] = remove_list
        # 3. response (no need to response this group command)
        return None


# register
GroupCommandProcessor.register(command=GroupCommand.EXPEL, processor_class=ExpelCommandProcessor)
