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


from .processor import ContentProcessor
from .forward import ForwardContentProcessor
from .file import FileContentProcessor

from .command import CommandProcessor
from .history import HistoryCommandProcessor, GroupCommandProcessor
from .invite import InviteCommandProcessor
from .expel import ExpelCommandProcessor
from .quit import QuitCommandProcessor
from .reset import ResetCommandProcessor
from .query import QueryCommandProcessor

from .meta import MetaCommandProcessor
from .profile import ProfileCommandProcessor


__all__ = [
    'ContentProcessor',
    'ForwardContentProcessor',
    'FileContentProcessor',

    'CommandProcessor',

    'HistoryCommandProcessor', 'GroupCommandProcessor',
    'InviteCommandProcessor', 'ExpelCommandProcessor', 'QuitCommandProcessor',
    'ResetCommandProcessor', 'QueryCommandProcessor',

    'MetaCommandProcessor',
    'ProfileCommandProcessor',
]
