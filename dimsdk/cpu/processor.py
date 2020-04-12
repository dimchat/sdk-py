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
from typing import Optional, Union

from dimp import ID
from dimp import ReliableMessage
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

    def get_context(self, key: str):
        return self.messenger.get_context(key)

    def set_context(self, key: str, value):
        return self.messenger.set_context(key=key, value=value)

    #
    #   Runtime
    #
    def _create_processor(self, clazz):
        assert issubclass(clazz, ContentProcessor), 'cpu class error: %s' % clazz
        return clazz(self.messenger)

    __content_processor_classes = {}  # class map

    @classmethod
    def register(cls, content_type: Union[ContentType, int], processor_class=None) -> bool:
        if isinstance(content_type, ContentType):
            content_type = content_type.value
        if processor_class is None:
            cls.__content_processor_classes.pop(content_type, None)
        elif processor_class == ContentProcessor:
            raise TypeError('should not add ContentProcessor itself!')
        else:
            assert issubclass(processor_class, ContentProcessor), 'cpu class error: %s' % processor_class
            cls.__content_processor_classes[content_type] = processor_class
        return True

    def cpu(self, content_type: Union[ContentType, int]):
        if isinstance(content_type, ContentType):
            content_type = content_type.value
        # 1. get from pool
        processor = self.__content_processors.get(content_type)
        if processor is not None:
            return processor
        # 2. get CPU class by content type
        clazz = self.__content_processor_classes.get(content_type)
        if clazz is None:
            if ContentType.Unknown == content_type:
                raise LookupError('default CPU not register yet')
            # call default CPU
            return self.cpu(content_type=ContentType.Unknown)
        # 3. create CPU with messenger
        processor = self._create_processor(clazz)
        assert processor is not None, 'failed to create CPU for content type: %s' % content_type
        self.__content_processors[content_type] = processor
        return processor

    #
    #   main
    #
    def process(self, content: Content, sender: ID, msg: ReliableMessage) -> Optional[Content]:
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
    def process(self, content: Content, sender: ID, msg: ReliableMessage) -> Content:
        res = TextContent.new(text='Content (type: %s) not support yet!' % content.type)
        # check group message
        group = content.group
        if group is not None:
            res.group = group
        return res


# register
ContentProcessor.register(content_type=ContentType.Unknown, processor_class=_DefaultContentProcessor)
