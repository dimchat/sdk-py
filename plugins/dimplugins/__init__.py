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

from .coder import *
from .digest import *
from .factories import *

from .network import NetworkType
from .entity import EntityID, EntityIDFactory


#
#   Register
#


def register_symmetric_key_factories():
    # Symmetric Key: AES
    factory = GeneralSymmetricFactory(algorithm=SymmetricKey.AES)
    SymmetricKey.register(algorithm=SymmetricKey.AES, factory=factory)
    SymmetricKey.register(algorithm='AES/CBC/PKCS7Padding', factory=factory)

    # Symmetric Key: Plain
    factory = GeneralSymmetricFactory(algorithm=PlainKey.PLAIN)
    SymmetricKey.register(algorithm=PlainKey.PLAIN, factory=factory)


def register_asymmetric_key_factories():
    # Public Key: ECC
    pub_fact = GeneralPublicFactory()
    PublicKey.register(algorithm=AsymmetricKey.ECC, factory=pub_fact)
    # Public Key: RSA
    PublicKey.register(algorithm=AsymmetricKey.RSA, factory=pub_fact)
    PublicKey.register(algorithm='SHA256withRSA', factory=pub_fact)
    PublicKey.register(algorithm='RSA/ECB/PKCS1Padding', factory=pub_fact)

    # Private Key: ECC
    ecc_fact = GeneralPrivateFactory(algorithm=AsymmetricKey.ECC)
    PrivateKey.register(algorithm=AsymmetricKey.ECC, factory=ecc_fact)

    # Private Key: RSA
    rsa_fact = GeneralPrivateFactory(algorithm=AsymmetricKey.RSA)
    PrivateKey.register(algorithm=AsymmetricKey.RSA, factory=rsa_fact)
    PrivateKey.register(algorithm='SHA256withRSA', factory=rsa_fact)
    PrivateKey.register(algorithm='RSA/ECB/PKCS1Padding', factory=rsa_fact)


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
    Document.register(doc_type='*', factory=GeneralDocumentFactory(doc_type='*'))
    Document.register(doc_type=Document.VISA, factory=GeneralDocumentFactory(doc_type=Document.VISA))
    Document.register(doc_type=Document.PROFILE, factory=GeneralDocumentFactory(doc_type=Document.PROFILE))
    Document.register(doc_type=Document.BULLETIN, factory=GeneralDocumentFactory(doc_type=Document.BULLETIN))


#
#   Register all factories
#
register_symmetric_key_factories()
register_asymmetric_key_factories()

register_id_factory()
register_address_factory()
register_meta_factories()
register_document_factories()


__all__ = [

    'RSAPublicKey', 'RSAPrivateKey',
    'ECCPublicKey', 'ECCPrivateKey',
    'AESKey',
    'PlainKey',

    # 'GeneralPublicFactory', 'GeneralPrivateFactory',
    # 'GeneralSymmetricFactory',
    # 'GeneralAddressFactory',
    # 'GeneralMetaFactory',
    # 'GeneralDocumentFactory',

    # 'NetworkType',
    # 'EntityID', 'EntityIDFactory',

    'BTCAddress', 'ETHAddress',
    'DefaultMeta', 'BTCMeta', 'ETHMeta',
]
