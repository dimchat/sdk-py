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

from .network import ServiceProvider, Station, Robot

from .group import Polylogue

from .protocol import ReceiptCommand, HandshakeCommand, LoginCommand
from .protocol import BlockCommand, MuteCommand, StorageCommand

from .cpu import ContentProcessor, ForwardContentProcessor, FileContentProcessor
from .cpu import CommandProcessor, HistoryCommandProcessor, GroupCommandProcessor
from .cpu import InviteCommandProcessor, ExpelCommandProcessor, QuitCommandProcessor
from .cpu import ResetCommandProcessor, QueryCommandProcessor
from .cpu import MetaCommandProcessor, DocumentCommandProcessor

from .delegate import Callback, CompletionHandler, MessengerDelegate

from .facebook import Facebook
from .messenger import Messenger

from .ans import AddressNameService

name = 'DIM-SDK'

__author__ = 'Albert Moky'

__all__ = [

    #
    #   Crypto
    #
    'DataCoder', 'Base64', 'Base58', 'Hex',
    'base64_encode', 'base64_decode', 'base58_encode', 'base58_decode', 'hex_encode', 'hex_decode',
    'DataParser', 'JSON', 'UTF8',
    'json_encode', 'json_decode', 'utf8_encode', 'utf8_decode',

    'DataDigester', 'MD5', 'SHA1', 'SHA256', 'KECCAK256', 'RIPEMD160',
    'md5', 'sha1', 'sha256', 'keccak256', 'ripemd160',

    'SOMap', 'Dictionary', 'String',

    'CryptographyKey', 'EncryptKey', 'DecryptKey',
    'AsymmetricKey', 'SignKey', 'VerifyKey',
    'PublicKey', 'PublicKeyFactory',
    'PrivateKey', 'PrivateKeyFactory',
    'SymmetricKey', 'SymmetricKeyFactory',

    #
    #   MingKeMing
    #
    'NetworkType', 'MetaType',
    'Address', 'AddressFactory',
    'ID', 'ANYONE', 'EVERYONE', 'ANYWHERE', 'EVERYWHERE',
    'Meta', 'BaseMeta', 'MetaFactory',
    'Document', 'BaseDocument', 'DocumentFactory',
    'Visa', 'BaseVisa', 'Bulletin', 'BaseBulletin',

    #
    #   DaoKeDao
    #
    'ContentType',
    'Content', 'BaseContent', 'ContentFactory',
    'Envelope',
    'Message',
    'InstantMessage', 'SecureMessage', 'ReliableMessage',
    'MessageDelegate',
    'InstantMessageDelegate', 'SecureMessageDelegate', 'ReliableMessageDelegate',

    #
    #   Protocol
    #
    'ForwardContent', 'TextContent',
    'FileContent', 'ImageContent', 'AudioContent', 'VideoContent',

    'Command', 'HistoryCommand', 'GroupCommand',
    'InviteCommand', 'ExpelCommand', 'JoinCommand', 'QuitCommand',
    'QueryCommand', 'ResetCommand',

    'MetaCommand', 'DocumentCommand',

    #
    #   Core
    #
    'Entity', 'EntityDataSource',
    'User', 'UserDataSource',
    'Group', 'GroupDataSource',

    'EntityDelegate', 'CipherKeyDelegate',

    'Barrack', 'Packer', 'Processor', 'Transceiver',

    #
    #   DIM SDK
    #

    # network
    'ServiceProvider', 'Station', 'Robot',

    # group
    'Polylogue',

    # protocol
    'ReceiptCommand', 'HandshakeCommand', 'LoginCommand',
    'BlockCommand', 'MuteCommand', 'StorageCommand',

    # cpu
    'ContentProcessor', 'ForwardContentProcessor', 'FileContentProcessor',
    'CommandProcessor', 'HistoryCommandProcessor', 'GroupCommandProcessor',
    'InviteCommandProcessor', 'ExpelCommandProcessor', 'QuitCommandProcessor',
    'ResetCommandProcessor', 'QueryCommandProcessor',
    'MetaCommandProcessor', 'DocumentCommandProcessor',

    # delegate
    'Callback', 'CompletionHandler', 'MessengerDelegate',

    'Facebook', 'Messenger',
    'AddressNameService',

    #
    #  Sub Modules
    #

    #  1. dos
    #  2. apns
    #  3. notifications
    #  4. plugins
    #  5. immortals
]
