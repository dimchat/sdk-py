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

from dimp import ID
from dimp import InstantMessage
from dimp import ContentType, Content, TextContent
from dimp import HistoryCommand, GroupCommand


class ContentProcessor:

    DEBUG = True

    def __init__(self, context: dict):
        super().__init__()
        from ..messenger import Messenger
        from ..facebook import Facebook
        # sub-content processing units pool
        self.__pool: dict = {}
        # context
        self.context: dict = context
        # messenger
        self.messenger: Messenger = context.get('messenger')
        # facebook
        facebook = context.get('facebook')
        if facebook is None:
            self.facebook: Facebook = self.messenger.barrack
        else:
            self.facebook: Facebook = facebook

    def info(self, msg: str):
        if self.DEBUG:
            print('%s:\t%s' % (self.__class__.__name__, msg))

    def error(self, msg: str):
        if self.DEBUG:
            print('%s ERROR:\t%s' % (self.__class__.__name__, msg))

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
    def cpu_class(cls, content_type: ContentType):
        clazz = cls.__content_processor_classes.get(content_type)
        if clazz is None:
            # processor not defined, use default
            clazz = cls.__content_processor_classes[DefaultContentType]
        assert issubclass(clazz, ContentProcessor), 'error: %d, %s' % (content_type, clazz)
        return clazz

    def cpu(self, content_type: ContentType):
        processor = self.__pool.get(content_type)
        if processor is not None:
            # got from cache
            return processor
        # try to create new processor with content type
        clazz = self.cpu_class(content_type=content_type)
        assert clazz is not None, 'failed to get content processor class: %d' % content_type
        processor = clazz(context=self.context)
        self.__pool[content_type] = processor
        return processor

    #
    #   main
    #
    def process(self, content: Content, sender: ID, msg: InstantMessage) -> Content:
        if type(self) != ContentProcessor:
            raise AssertionError('override me!')
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
                    raise LookupError('group meta not found: %s' % group)
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
        assert cpu is not self, 'Dead cycle! content: %s' % content
        return cpu.process(content=content, sender=sender, msg=msg)


#
#   Default Content Processor
#
class _DefaultContentProcessor(ContentProcessor):

    #
    #   main
    #
    def process(self, content: Content, sender: ID, msg: InstantMessage) -> Content:
        if type(self) != _DefaultContentProcessor:
            raise AssertionError('override me!')
        return TextContent.new(text='content (type: %d) not support yet!' % content.type)


# register
DefaultContentType = ContentType(0)
ContentProcessor.register(content_type=DefaultContentType, processor_class=_DefaultContentProcessor)
