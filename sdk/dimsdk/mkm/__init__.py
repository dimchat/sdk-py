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

from .delegate import EntityDelegate
from .entity import EntityDataSource
from .entity import Entity, BaseEntity

from .group import GroupDataSource
from .group import Group, BaseGroup

from .user import UserDataSource
from .user import User, BaseUser

from .station import ServiceProvider, Station
from .bot import Bot

from .utils import MetaUtils, DocumentUtils

__all__ = [

    'EntityDelegate',
    'EntityDataSource',
    'Entity', 'BaseEntity',

    'GroupDataSource',
    'Group', 'BaseGroup',

    'UserDataSource',
    'User', 'BaseUser',

    'ServiceProvider',
    'Station',
    'Bot',

    'MetaUtils', 'DocumentUtils',

]
