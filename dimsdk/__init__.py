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

from dimp import *

from .plugins import *

from .notification import Notification, Observer, NotificationCenter
from .notification import ApplePushNotificationService

from .network import CASubject, CAValidity, CAData, CertificateAuthority
from .network import ServiceProvider, Station, Robot

from .group import Polylogue

from .protocol import ReceiptCommand, HandshakeCommand, LoginCommand
from .protocol import BlockCommand, MuteCommand, StorageCommand

from .cpu import ContentProcessor, ForwardContentProcessor
from .cpu import CommandProcessor, HistoryCommandProcessor, GroupCommandProcessor
from .cpu import InviteCommandProcessor, ExpelCommandProcessor, QuitCommandProcessor
from .cpu import ResetCommandProcessor, QueryCommandProcessor
from .cpu import MetaCommandProcessor, ProfileCommandProcessor

from .delegate import Callback, CompletionHandler, MessengerDelegate

from .ans import AddressNameService
from .facebook import Facebook
from .keystore import KeyStore
from .messenger import Messenger

name = 'DIM-SDK'

__author__ = 'Albert Moky'

__all__ = [

    #
    #   MingKeMing
    #

    # crypto
    'SignKey', 'VerifyKey', 'EncryptKey', 'DecryptKey',
    'SymmetricKey', 'PrivateKey', 'PublicKey',

    # data
    'BaseCoder',
    'Base64', 'Base58', 'Hex',
    'Digest',
    'MD5', 'SHA1', 'SHA256', 'RIPEMD160',
    'md5', 'sha1', 'sha256', 'ripemd160',

    # entity
    'NetworkID', 'MetaVersion',
    'Address', 'ID', 'Meta', 'Profile',
    'Entity', 'User', 'Group',

    # delegate
    'EntityDataSource', 'UserDataSource', 'GroupDataSource',

    'ANYONE', 'EVERYONE', 'ANYWHERE', 'EVERYWHERE',

    #
    #   DaoKeDao
    #

    # message
    'Envelope', 'Content', 'Message',

    # content types
    'ContentType', 'ForwardContent',

    # transform
    'InstantMessage', 'SecureMessage', 'ReliableMessage',

    # delegate
    'InstantMessageDelegate', 'SecureMessageDelegate', 'ReliableMessageDelegate',

    #
    #   DIMP
    #

    # protocol
    'TextContent', 'FileContent', 'ImageContent', 'AudioContent', 'VideoContent',
    'Command', 'HistoryCommand', 'GroupCommand',
    'InviteCommand', 'ExpelCommand', 'JoinCommand', 'QuitCommand',
    'QueryCommand', 'ResetCommand',
    'MetaCommand', 'ProfileCommand',

    # core
    'Barrack', 'KeyCache', 'Transceiver',

    # delegate
    'EntityDelegate', 'CipherKeyDelegate',

    #
    #   DIM SDK
    #

    # notification
    'Notification', 'Observer', 'NotificationCenter',
    'ApplePushNotificationService',

    # network
    'CASubject', 'CAValidity', 'CAData', 'CertificateAuthority',
    'ServiceProvider', 'Station', 'Robot',

    # group
    'Polylogue',

    # protocol
    'ReceiptCommand', 'HandshakeCommand', 'LoginCommand',
    'BlockCommand', 'MuteCommand', 'StorageCommand',

    # cpu
    'ContentProcessor', 'ForwardContentProcessor',
    'CommandProcessor', 'HistoryCommandProcessor', 'GroupCommandProcessor',
    'InviteCommandProcessor', 'ExpelCommandProcessor', 'QuitCommandProcessor',
    'ResetCommandProcessor', 'QueryCommandProcessor',
    'MetaCommandProcessor', 'ProfileCommandProcessor',

    # delegate
    'Callback', 'CompletionHandler', 'MessengerDelegate',

    'AddressNameService', 'Facebook', 'KeyStore', 'Messenger',
]
