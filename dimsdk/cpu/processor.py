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
    Content Processor
    ~~~~~~~~~~~~~~~~~

"""

from dimp import Envelope, Content, ContentType
from dimp import HistoryCommand, GroupCommand


class ContentProcessor:

    def __init__(self, messenger):
        super().__init__()
        from ..messenger import Messenger
        from ..facebook import Facebook
        self.messenger: Messenger = messenger
        self.facebook: Facebook = messenger.barrack
        # content processing units
        self.__processors = {}

    def info(self, msg: str):
        print('%s:\t%s' % (self.__class__.__name__, msg))

    def error(self, msg: str):
        print('%s ERROR:\t%s' % (self.__class__.__name__, msg))

    def cpu(self, content_type: ContentType):
        cpu = self.__processors.get(content_type)
        if cpu is not None:
            return cpu
        # try to create new processor
        clazz = self.processor_class(content_type=content_type)
        if clazz is not None:
            cpu = clazz(self.messenger)
            self.__processors[content_type] = cpu
            return cpu

    def process(self, content: Content, envelope: Envelope) -> bool:
        if type(self) != ContentProcessor:
            raise AssertionError('override me!')
        sender = self.facebook.identifier(envelope.sender)
        group = self.facebook.identifier(content.group)
        if group is not None:
            # check meta for new group ID
            if not group.is_broadcast:
                # check meta
                meta = self.facebook.meta(identifier=group)
                if meta is None:
                    # NOTICE: if meta for group not found,
                    #         the client will query it automatically
                    # TODO: insert the message to a temporary queue to waiting meta
                    return False
            # check whether the group members info needs update
            grp = self.facebook.group(identifier=group)
            assert grp is not None, 'group meta error: %s' % group
            # if the group info not found, and this is not an 'invite' command
            #     query group info from the sender
            needs_update = grp.founder is None
            if isinstance(content, HistoryCommand):
                if GroupCommand.INVITE == content.command:
                    # FIXME: can we trust this stranger?
                    #        may be we should keep this members list temporary,
                    #        and send 'query' to the founder immediately.
                    # TODO: check whether the members list is a full list,
                    #       it should contain the group owner(founder)
                    needs_update = False
            if needs_update:
                query = GroupCommand.query(group=group)
                self.messenger.send_content(content=query, receiver=sender)
        # process content by type
        cpu: ContentProcessor = self.cpu(content_type=content.type)
        if cpu is None:
            self.error('content (type: %d) not support yet!' % content.type)
            return False
        if cpu is self:
            raise AssertionError('Dead cycle! content: %s' % content)
        try:
            # process by subclass
            return cpu.process(content=content, envelope=envelope)
        except Exception as error:
            self.error('content error: %s' % error)
            return False

    #
    #   Runtime
    #
    __content_processor_classes = {}  # class map

    @classmethod
    def register(cls, content_type: ContentType, processor_class=None) -> bool:
        if processor_class is None:
            cls.__content_processor_classes.pop(content_type, None)
        elif issubclass(processor_class, ContentProcessor):
            cls.__content_processor_classes[content_type] = processor_class
        else:
            raise TypeError('%s must be subclass of ContentProcessor' % processor_class)
        return True

    @classmethod
    def processor_class(cls, content_type: ContentType):
        return cls.__content_processor_classes.get(content_type)
