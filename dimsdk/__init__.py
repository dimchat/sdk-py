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

from .crypto import *
from .mkm import *
from .msg import *
from .dkd import *

from .core import *
from .base import *

from .cpu import *


name = 'DIM-SDK'

__author__ = 'Albert Moky'


__all__ = [

    'Singleton',

    'final',

    'StrMap', 'MutableStrMap',
    'AnyList', 'StrList',

    'URI', 'DateTime',

    'Converter', 'DataConverter', 'BaseConverter',
    'Copier', 'DataCopier', 'BaseCopier',
    'Wrapper', 'DataWrapper', 'BaseWrapper',

    'Stringer', 'Mapper',
    'ConstantString',  # 'String',

    'Dictionary',

    #
    #   Format
    #

    'DataCoder', 'Hex', 'Base58', 'Base64',
    'ObjectCoder', 'JSON',
    'MapCoder', 'JSONMap',
    'StringCoder', 'UTF8',

    'TransportableResource',
    'TransportableData',

    'TransportableDataFactory',

    'TransportableDataHelper',
    'FormatExtensions', 'shared_format_extensions',

    #
    #   TED
    #

    'BaseString', 'BaseData',

    'PlainData',

    #
    #   PNF
    #

    'TransportableFile', 'TransportableFileFactory',
    'TransportableFileWrapper', 'TransportableFileWrapperFactory',
    'TransportableFileHelper',

    # ================================================================

    #
    #   Digest
    #

    'MessageDigester',
    'SHA256', 'KECCAK256', 'RIPEMD160',

    #
    #   Crypto
    #

    'CryptographyKey',
    'EncryptKey', 'DecryptKey', 'SignKey', 'VerifyKey',
    'SymmetricKey', 'AsymmetricKey',
    'PrivateKey', 'PublicKey',

    'SymmetricKeyFactory', 'PrivateKeyFactory', 'PublicKeyFactory',

    'SymmetricKeyHelper', 'PublicKeyHelper', 'PrivateKeyHelper',

    'SymmetricKeyExtension', 'PublicKeyExtension', 'PrivateKeyExtension',
    'CryptoExtensions', 'shared_crypto_extensions',

    #
    #   Encrypted Key Bundle
    #

    'BytesMap',

    'EncryptedBundle', 'UserEncryptedBundle',

    'EncryptedBundleHandler', 'DefaultBundleHandler',
    'BundleExtension',

    # ================================================================

    #
    #   Ming-Ke-Ming
    #

    'EntityType',
    'Address', 'ID',
    'Meta', 'TAI', 'Document',

    'AddressFactory', 'IDFactory',
    'MetaFactory', 'DocumentFactory',

    'ANYWHERE', 'EVERYWHERE',
    'ANYONE', 'EVERYONE', 'FOUNDER',
    # 'BroadcastAddress',
    'Identifier',

    'AddressHelper', 'IDHelper',
    'MetaHelper', 'DocumentHelper',

    'AddressExtension', 'IDExtension',
    'MetaExtension', 'DocumentExtension',
    'AccountExtensions', 'shared_account_extensions',

    'CryptoKeyHandler', 'GeneralCryptoExtension',
    'AccountHandler', 'GeneralAccountExtension',

    #
    #   Dao-Ke-Dao
    #

    'Content', 'Envelope',
    'Message',
    'InstantMessage', 'SecureMessage', 'ReliableMessage',

    'ContentFactory', 'EnvelopeFactory',
    'InstantMessageFactory', 'SecureMessageFactory', 'ReliableMessageFactory',

    'ContentHelper', 'EnvelopeHelper',
    'InstantMessageHelper', 'SecureMessageHelper', 'ReliableMessageHelper',

    'ContentExtension',
    'InstantMessageExtension', 'SecureMessageExtension', 'ReliableMessageExtension',
    'MessageExtensions', 'shared_message_extensions',

    'MessageHandler', 'MessageHandlerExtension',

    #
    #   Core Protocols
    #

    'ContentType',

    'Command', 'CommandFactory',

    'CommandHelper', 'CommandHandler',
    'CommandExtension', 'GeneralCommandExtension',

    #
    #   Message Implementations
    #

    'MessageEnvelope',
    'BaseMessage',
    'PlainMessage', 'EncryptedMessage', 'NetworkMessage',



    ################################################################
    #
    #   Software Development Kits
    #
    ################################################################


    'VisaAgent', 'DefaultVisaAgent',
    'VisaAgentExtension',

    #
    #   Entities (MingKeMing)
    #

    'EntityDelegate',
    'EntityDataSource',
    'Entity', 'BaseEntity',

    'GroupDataSource',
    'Group', 'BaseGroup',

    'UserDataSource',
    'User', 'BaseUser',

    #
    #   Message Transformers (DaoKeDao)
    #

    'InstantMessageDelegate',
    'SecureMessageDelegate',
    'ReliableMessageDelegate',

    'InstantMessagePacker',
    'SecureMessagePacker',
    'ReliableMessagePacker',

    'MessagePackerFactory',
    'MessagePackerExtension',

    #
    #   Content Processors (DaoKeDao)
    #

    'ContentProcessor',
    'ContentProcessorCreator',
    'ContentProcessorFactory',

    'GeneralContentProcessorFactory',

    #
    #   Compressor (Short Key + JSON + UTF8 Encoding)
    #

    'Shortener', 'MessageShortener',
    'Compressor', 'MessageCompressor',

    #
    #   Core Interfaces
    #

    'Barrack',

    'Packer',
    'Processor',
    'Transformer',

    'CipherKeyDelegate',

    #
    #   Twins
    #

    'TwinsHelper',

    'Facebook',

    'Messenger',
    'MessageProcessor',
    'MessagePacker',

    #
    #   CPU - Content Processing Units
    #

    'ContentProcessor',
    'ContentProcessorCreator',
    'ContentProcessorFactory',
    'GeneralContentProcessorFactory',

    'BaseContentProcessor', 'BaseCommandProcessor',
    'BaseContentProcessorCreator',

]
