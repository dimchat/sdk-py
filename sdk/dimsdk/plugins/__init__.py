# -*- coding: utf-8 -*-
#
#   DIM-SDK : Decentralized Instant Messaging Software Development Kit
#
#                                Written in 2024 by Moky <albert.moky@gmail.com>
#
# ==============================================================================
# MIT License
#
# Copyright (c) 2024 Albert Moky
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

from dimp.plugins import *

from .crypto import CryptographyKeyGeneralFactory
from .format import FormatGeneralFactory
from .account import AccountGeneralFactory
from .message import MessageGeneralFactory
from .command import CommandGeneralFactory

from .loader import ContentParser, CommandParser
from .loader import ExtensionLoader


__all__ = [

    #
    #   Crypto
    #

    'SymmetricKeyHelper', 'PublicKeyHelper', 'PrivateKeyHelper',
    # 'CryptoExtensions',

    'GeneralCryptoHelper', 'SharedCryptoExtensions',

    #
    #   Format
    #

    'TransportableDataHelper', 'PortableNetworkFileHelper',
    # 'FormatExtensions',

    'GeneralFormatHelper', 'SharedFormatExtensions',

    #
    #   Account
    #

    'AddressHelper', 'IdentifierHelper',
    'MetaHelper', 'DocumentHelper',
    # 'AccountExtensions',

    'GeneralAccountHelper', 'SharedAccountExtensions',

    #
    #   Message
    #

    'ContentHelper', 'EnvelopeHelper',
    'InstantMessageHelper', 'SecureMessageHelper', 'ReliableMessageHelper',
    # 'MessageExtensions',

    'GeneralMessageHelper', 'SharedMessageExtensions',

    #
    #   Command
    #

    'CommandHelper',
    # 'CommandExtensions',

    'GeneralCommandHelper', 'SharedCommandExtensions',

    #
    #   Core Extensions
    #

    'CryptographyKeyGeneralFactory', 'FormatGeneralFactory',
    'AccountGeneralFactory',
    'MessageGeneralFactory', 'CommandGeneralFactory',

    'ContentParser', 'CommandParser',
    'ExtensionLoader',

]
