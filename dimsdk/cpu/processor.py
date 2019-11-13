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

import weakref
from typing import Optional

from dimp import ID
from dimp import InstantMessage
from dimp import ContentType, Content, TextContent


class ContentProcessor:

    def __init__(self, messenger):
        super().__init__()
        self.__content_processors: dict = {}
        self.__messenger = weakref.ref(messenger)

    @property
    def messenger(self):  # Messenger
        return self.__messenger()

    @property
    def facebook(self):  # Facebook
        return self.messenger.facebook

    #
    #   Runtime
    #
    def _create_processor(self, clazz):
        assert issubclass(clazz, ContentProcessor), 'cpu class error: %s' % clazz
        return clazz(self.messenger)

    __content_processor_classes = {}  # class map

    @classmethod
    def register(cls, content_type: ContentType, processor_class=None) -> bool:
        if processor_class is None:
            cls.__content_processor_classes.pop(content_type, None)
        elif processor_class == ContentProcessor:
            raise TypeError('should not add ContentProcessor itself!')
        else:
            assert issubclass(processor_class, ContentProcessor), 'cpu class error: %s' % processor_class
            cls.__content_processor_classes[content_type] = processor_class
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
        processor = self.__content_processors.get(content_type)
        if processor is None:
            # try to create new processor with content type
            clazz = self.cpu_class(content_type=content_type)
            assert clazz is not None, 'failed to get content processor class: %d' % content_type
            processor = self._create_processor(clazz)
            self.__content_processors[content_type] = processor
        return processor

    #
    #   main
    #
    def process(self, content: Content, sender: ID, msg: InstantMessage) -> Optional[Content]:
        assert type(self) == ContentProcessor, 'override me!'
        # process content by type
        cpu = self.cpu(content_type=content.type)
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
        return TextContent.new(text='Content (type: %d) not support yet!' % content.type)


# register
DefaultContentType = ContentType.Unknown
ContentProcessor.register(content_type=DefaultContentType, processor_class=_DefaultContentProcessor)
