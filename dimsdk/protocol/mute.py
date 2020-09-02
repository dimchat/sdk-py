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
    Mute Protocol
    ~~~~~~~~~~~~~

    Mute all messages(skip Pushing Notification) in this conversation, which ID(user/group) contains in 'list'.
    If value of 'list' is None, means querying mute-list from station
"""

from typing import Optional

from dimp import Command


class MuteCommand(Command):
    """
        Mute Command
        ~~~~~~~~~~~~

        data format: {
            type : 0x88,
            sn   : 123,

            command : "mute", // command name
            list    : []      // mute-list
        }
    """

    MUTE = 'mute'

    def __new__(cls, cmd: dict):
        """
        Create mute command

        :param cmd: command info
        :return: MuteCommand object
        """
        if cmd is None:
            return None
        elif cls is MuteCommand:
            if isinstance(cmd, MuteCommand):
                # return MuteCommand object directly
                return cmd
        # new MuteCommand(dict)
        return super().__new__(cls, cmd)

    def __init__(self, content: dict):
        if self is content:
            # no need to init again
            return
        super().__init__(content)

    #
    #   mute-list
    #
    @property
    def mute_list(self) -> Optional[list]:
        return self.get('list')

    @mute_list.setter
    def mute_list(self, value: list):
        if value is None:
            self.pop('list', None)
        else:
            self['list'] = value

    #
    #   Factories
    #
    @classmethod
    def new(cls, content: dict=None, mute: list=None, time: int=0):
        """
        Create mute command

        :param content: command info
        :param mute: mute-list
        :param time: command time
        :return: MuteCommand object
        """
        if content is None:
            # create empty content
            content = {}
        # set mute-list
        if mute is not None:
            content['list'] = mute
        # new MuteCommand(dict)
        return super().new(content=content, command=cls.MUTE, time=time)


# register command class
Command.register(command=MuteCommand.MUTE, command_class=MuteCommand)
