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
    Meta Command Processor
    ~~~~~~~~~~~~~~~~~~~~~~

"""

from typing import Optional

from dimp import ID, Meta
from dimp import ReliableMessage
from dimp import Content
from dimp import TextContent, Command, MetaCommand

from ..protocol import ReceiptCommand

from .command import CommandProcessor


class MetaCommandProcessor(CommandProcessor):

    def __get(self, identifier: ID) -> Content:
        # query meta for ID
        meta = self.facebook.meta(identifier=identifier)
        if meta is None:
            # meta not found
            return TextContent.new(text='Sorry, meta for %s not found.' % identifier)
        # response
        return MetaCommand.response(identifier=identifier, meta=meta)

    def __put(self, identifier: ID, meta: Meta) -> Content:
        facebook = self.facebook
        # received a meta for ID
        if not facebook.verify_meta(meta=meta, identifier=identifier):
            # meta not match
            return TextContent.new(text='Meta not match ID: %s' % identifier)
        if not facebook.save_meta(meta=meta, identifier=identifier):
            # save meta failed
            return TextContent.new(text='Meta not accept: %s!' % identifier)
        # response
        return ReceiptCommand.new(message='Meta received: %s' % identifier)

    #
    #   main
    #
    def process(self, content: Content, sender: ID, msg: ReliableMessage) -> Optional[Content]:
        assert isinstance(content, MetaCommand), 'command error: %s' % content
        identifier = content.identifier
        meta = content.meta
        if meta is None:
            return self.__get(identifier=identifier)
        else:
            return self.__put(identifier=identifier, meta=meta)


# register
CommandProcessor.register(command=Command.META, processor_class=MetaCommandProcessor)
