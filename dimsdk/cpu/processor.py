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

from typing import Optional

from dimp import ID
from dimp import InstantMessage
from dimp import ContentType, Content, TextContent
from dimp import GroupCommand, InviteCommand


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
        self.messenger: Messenger = context['messenger']
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
        if processor is None:
            # try to create new processor with content type
            clazz = self.cpu_class(content_type=content_type)
            assert clazz is not None, 'failed to get content processor class: %d' % content_type
            processor = clazz(context=self.context)
            self.__pool[content_type] = processor
        return processor

    #
    #   main
    #
    def process(self, content: Content, sender: ID, msg: InstantMessage) -> Optional[Content]:
        assert type(self) == ContentProcessor, 'override me!'
        assert isinstance(content, Content), 'message content error: %s' % content
        self.__check_group(content=content, sender=sender)
        # process content by type
        cpu: ContentProcessor = self.cpu(content_type=content.type)
        assert cpu is not self, 'Dead cycle! content: %s' % content
        return cpu.process(content=content, sender=sender, msg=msg)

    def __check_group(self, content: Content, sender: ID) -> bool:
        """
        Check if it is a group message, and whether the group members info needs update

        :param content: message content
        :param sender:  message sender
        :return: True on updating
        """
        group = self.facebook.identifier(content.group)
        if group is None or group.is_broadcast:
            # 1. personal message
            # 2. broadcast message
            return False
        # check meta for new group ID
        meta = self.facebook.meta(identifier=group)
        if meta is None:
            # NOTICE: if meta for group not found,
            #         facebook should query it from DIM network automatically
            # TODO: insert the message to a temporary queue to wait meta
            raise LookupError('group meta not found: %s' % group)
        # NOTICE: if the group info not found, and this is not an 'invite' command
        #         query group info from the sender
        needs_update = self.__is_empty(group=group)
        if isinstance(content, InviteCommand):
            # FIXME: can we trust this stranger?
            #        may be we should keep this members list temporary,
            #        and send 'query' to the owner immediately.
            # TODO: check whether the members list is a full list,
            #       it should contain the group owner(owner)
            needs_update = False
        if needs_update:
            query = GroupCommand.query(group=group)
            return self.messenger.send_content(content=query, receiver=sender)

    def __is_empty(self, group: ID) -> bool:
        """
        Check whether group info empty (lost)

        :param group: group ID
        :return: True on members, owner not found
        """
        members = self.facebook.members(identifier=group)
        if members is None or len(members) == 0:
            return True
        owner = self.facebook.owner(identifier=group)
        if owner is None:
            return True


#
#   Default Content Processor
#
class _DefaultContentProcessor(ContentProcessor):

    #
    #   main
    #
    def process(self, content: Content, sender: ID, msg: InstantMessage) -> Content:
        return TextContent.new(text='content (type: %d) not support yet!' % content.type)


# register
DefaultContentType = ContentType.Unknown
ContentProcessor.register(content_type=DefaultContentType, processor_class=_DefaultContentProcessor)
