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
    Content/Command Processing Units
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from .base import TwinsHelper

from .base import ContentProcessor
from .base import ContentProcessorCreator
from .base import ContentProcessorFactory

from .creator import BaseContentProcessorCreator
from .factory import GeneralContentProcessorFactory

from .base import BaseContentProcessor
from .base import BaseCommandProcessor

from .contents import ForwardContentProcessor
from .contents import ArrayContentProcessor

from .commands import MetaCommandProcessor
from .commands import DocumentCommandProcessor
from .commands import ReceiptCommandProcessor

from .customized import CustomizedContentProcessor
from .customized import CustomizedContentHandler


__all__ = [

    'TwinsHelper',

    'ContentProcessor',
    'ContentProcessorCreator',
    'ContentProcessorFactory',

    'BaseContentProcessorCreator',
    'GeneralContentProcessorFactory',

    'BaseContentProcessor',
    'BaseCommandProcessor',

    'ForwardContentProcessor',
    'ArrayContentProcessor',

    'MetaCommandProcessor',
    'DocumentCommandProcessor',
    'ReceiptCommandProcessor',

    'CustomizedContentProcessor',
    'CustomizedContentHandler',
]
