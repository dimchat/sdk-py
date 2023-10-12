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
    Decentralized Instant Messaging (Python Plugins)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from .format import Base64Data, Base64DataFactory
from .format import BaseNetworkFile, BaseNetworkFileFactory

from .crypto import PlainKey, PlainKeyFactory
from .crypto import AESKey, AESKeyFactory
from .crypto import RSAPublicKey, RSAPublicKeyFactory
from .crypto import RSAPrivateKey, RSAPrivateKeyFactory
from .crypto import ECCPublicKey, ECCPublicKeyFactory
from .crypto import ECCPrivateKey, ECCPrivateKeyFactory

from .mkm import BTCAddress, ETHAddress
from .mkm import DefaultMeta, BTCMeta, ETHMeta
from .mkm import BaseAddressFactory, GeneralAddressFactory
from .mkm import GeneralIdentifierFactory, GeneralMetaFactory, GeneralDocumentFactory

from .format import register_data_coders
from .crypto import register_data_digesters
from .crypto import register_symmetric_key_factories
from .crypto import register_asymmetric_key_factories

from .mkm import register_address_factory
from .mkm import register_identifier_factory
from .mkm import register_meta_factories
from .mkm import register_document_factories


#
#   Register
#


def register_plugins():
    """ Register all factories """
    register_data_coders()
    register_data_digesters()

    register_symmetric_key_factories()
    register_asymmetric_key_factories()

    register_identifier_factory()
    register_address_factory()
    register_meta_factories()
    register_document_factories()


__all__ = [

    #
    #   Format
    #
    'Base64Data', 'Base64DataFactory',
    'BaseNetworkFile', 'BaseNetworkFileFactory',

    #
    #   Crypto
    #

    'PlainKey', 'PlainKeyFactory',
    'AESKey', 'AESKeyFactory',

    'RSAPublicKey', 'RSAPublicKeyFactory',
    'RSAPrivateKey', 'RSAPrivateKeyFactory',

    'ECCPublicKey', 'ECCPublicKeyFactory',
    'ECCPrivateKey', 'ECCPrivateKeyFactory',

    #
    #   MingKeMing
    #

    'BTCAddress', 'ETHAddress',
    'DefaultMeta', 'BTCMeta', 'ETHMeta',

    'BaseAddressFactory', 'GeneralAddressFactory',
    'GeneralIdentifierFactory',
    'GeneralMetaFactory',
    'GeneralDocumentFactory',

    #
    #   Register
    #
    'register_data_coders', 'register_data_digesters',
    'register_symmetric_key_factories', 'register_asymmetric_key_factories',
    'register_identifier_factory', 'register_address_factory',
    'register_meta_factories', 'register_document_factories',
    'register_plugins',
]
