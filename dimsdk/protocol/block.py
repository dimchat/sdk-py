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
    Block Protocol
    ~~~~~~~~~~~~~~

    Ignore all messages in this conversation, which ID(user/group) contains in 'list'.
    If value of 'list' is None, means querying block-list from station
"""

from typing import Optional

from dimp import Command


class BlockCommand(Command):
    """
        Block Command
        ~~~~~~~~~~~~~

        data format: {
            type : 0x88,
            sn   : 123,

            command : "block", // command name
            list    : []       // block-list
        }
    """

    BLOCK = 'block'

    def __new__(cls, cmd: dict):
        """
        Create block command

        :param cmd: command info
        :return: BlockCommand object
        """
        if cmd is None:
            return None
        elif cls is BlockCommand:
            if isinstance(cmd, BlockCommand):
                # return BlockCommand object directly
                return cmd
        # new BlockCommand(dict)
        return super().__new__(cls, cmd)

    def __init__(self, content: dict):
        if self is content:
            # no need to init again
            return
        super().__init__(content)

    #
    #   block-list
    #
    @property
    def block_list(self) -> Optional[list]:
        return self.get('list')

    @block_list.setter
    def block_list(self, value: list):
        if value is None:
            self.pop('list', None)
        else:
            self['list'] = value

    #
    #   Factories
    #
    @classmethod
    def new(cls, content: dict=None, block: list=None, time: int=0):
        """
        Create block command

        :param content: command info
        :param block: block-list
        :param time: command time
        :return: BlockCommand object
        """
        if content is None:
            # create empty content
            content = {}
        # set block-list
        if block is not None:
            content['list'] = block
        # new BlockCommand(dict)
        return super().new(content=content, command=cls.BLOCK, time=time)


# register command class
Command.register(command=BlockCommand.BLOCK, command_class=BlockCommand)
