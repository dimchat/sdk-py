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

from mkm.crypto import SymmetricKey, AsymmetricKey, PublicKey, PrivateKey
from mkm import ID, Address
from mkm import MetaType, Meta, Document
from dimp import BaseDocumentFactory

from .keys import BaseKey, BaseSymmetricKey, BaseAsymmetricKey
from .keys import BasePublicKey, BasePrivateKey

from .plain import PlainKey
from .aes import AESKey
from .rsa import RSAPublicKey, RSAPrivateKey
from .ecc import ECCPublicKey, ECCPrivateKey

from .btc import BTCAddress
from .eth import ETHAddress
from .meta import DefaultMeta, BTCMeta, ETHMeta

from .factories import RSAPublicKeyFactory, RSAPrivateKeyFactory
from .factories import ECCPublicKeyFactory, ECCPrivateKeyFactory
from .factories import AESKeyFactory, PlainKeyFactory
from .factories import GeneralAddressFactory, GeneralMetaFactory

from .network import NetworkType
from .entity import EntityID
from .entity import EntityIDFactory

from .coder import register_data_coders
from .digest import register_data_digesters


#
#   Register
#


def register_symmetric_key_factories():
    # Symmetric Key: AES
    factory = AESKeyFactory()
    SymmetricKey.register(algorithm=SymmetricKey.AES, factory=factory)
    SymmetricKey.register(algorithm='AES/CBC/PKCS7Padding', factory=factory)

    # Symmetric Key: Plain
    factory = PlainKeyFactory()
    SymmetricKey.register(algorithm=PlainKey.PLAIN, factory=factory)


def register_asymmetric_key_factories():
    # Public Key: ECC
    factory = ECCPublicKeyFactory()
    PublicKey.register(algorithm=AsymmetricKey.ECC, factory=factory)
    # Public Key: RSA
    factory = RSAPublicKeyFactory()
    PublicKey.register(algorithm=AsymmetricKey.RSA, factory=factory)
    PublicKey.register(algorithm='SHA256withRSA', factory=factory)
    PublicKey.register(algorithm='RSA/ECB/PKCS1Padding', factory=factory)

    # Private Key: ECC
    factory = ECCPrivateKeyFactory()
    PrivateKey.register(algorithm=AsymmetricKey.ECC, factory=factory)

    # Private Key: RSA
    factory = RSAPrivateKeyFactory()
    PrivateKey.register(algorithm=AsymmetricKey.RSA, factory=factory)
    PrivateKey.register(algorithm='SHA256withRSA', factory=factory)
    PrivateKey.register(algorithm='RSA/ECB/PKCS1Padding', factory=factory)


def register_id_factory():
    ID.register(factory=EntityIDFactory())


def register_address_factory():
    Address.register(factory=GeneralAddressFactory())


def register_meta_factories():
    Meta.register(version=MetaType.MKM, factory=GeneralMetaFactory(version=MetaType.MKM))
    Meta.register(version=MetaType.BTC, factory=GeneralMetaFactory(version=MetaType.BTC))
    Meta.register(version=MetaType.ExBTC, factory=GeneralMetaFactory(version=MetaType.ExBTC))
    Meta.register(version=MetaType.ETH, factory=GeneralMetaFactory(version=MetaType.ETH))
    Meta.register(version=MetaType.ExETH, factory=GeneralMetaFactory(version=MetaType.ExETH))


def register_document_factories():
    Document.register(doc_type='*', factory=BaseDocumentFactory(doc_type='*'))
    Document.register(doc_type=Document.VISA, factory=BaseDocumentFactory(doc_type=Document.VISA))
    Document.register(doc_type=Document.PROFILE, factory=BaseDocumentFactory(doc_type=Document.PROFILE))
    Document.register(doc_type=Document.BULLETIN, factory=BaseDocumentFactory(doc_type=Document.BULLETIN))


def register_plugins():
    """ Register all factories """
    register_data_coders()
    register_data_digesters()

    register_symmetric_key_factories()
    register_asymmetric_key_factories()

    register_id_factory()
    register_address_factory()
    register_meta_factories()
    register_document_factories()


__all__ = [

    'BaseKey',
    'BaseSymmetricKey', 'BaseAsymmetricKey',
    'BasePublicKey', 'BasePrivateKey',

    'RSAPublicKey', 'RSAPrivateKey',
    'ECCPublicKey', 'ECCPrivateKey',
    'AESKey',
    'PlainKey',

    'RSAPublicKeyFactory', 'RSAPrivateKeyFactory',
    'ECCPublicKeyFactory', 'ECCPrivateKeyFactory',
    'AESKeyFactory', 'PlainKeyFactory',
    'GeneralAddressFactory',
    'GeneralMetaFactory',

    'NetworkType',
    'EntityID',
    'EntityIDFactory',

    'BTCAddress', 'ETHAddress',
    'DefaultMeta', 'BTCMeta', 'ETHMeta',

    'register_data_coders',
    'register_data_digesters',
    'register_symmetric_key_factories',
    'register_asymmetric_key_factories',
    'register_id_factory',
    'register_address_factory',
    'register_meta_factories',
    'register_document_factories',
    'register_plugins',
]
