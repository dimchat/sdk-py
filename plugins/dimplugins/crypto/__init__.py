# -*- coding: utf-8 -*-
# ==============================================================================
# MIT License
#
# Copyright (c) 2023 Albert Moky
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

from mkm.crypto import SymmetricKeyFactory, AsymmetricKey
from mkm.crypto import SymmetricKey, PublicKey, PrivateKey

from .plain import PlainKey, PlainKeyFactory
from .aes import AESKey, AESKeyFactory

from .rsa import RSAPublicKey, RSAPublicKeyFactory
from .rsa import RSAPrivateKey, RSAPrivateKeyFactory

from .ecc import ECCPublicKey, ECCPublicKeyFactory
from .ecc import ECCPrivateKey, ECCPrivateKeyFactory

from .digest import register_data_digesters


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
    PublicKey.register(algorithm='SHA256withECDSA', factory=factory)
    # Private Key: ECC
    factory = ECCPrivateKeyFactory()
    PrivateKey.register(algorithm=AsymmetricKey.ECC, factory=factory)
    PrivateKey.register(algorithm='SHA256withECDSA', factory=factory)

    # Public Key: RSA
    factory = RSAPublicKeyFactory()
    PublicKey.register(algorithm=AsymmetricKey.RSA, factory=factory)
    PublicKey.register(algorithm='SHA256withRSA', factory=factory)
    PublicKey.register(algorithm='RSA/ECB/PKCS1Padding', factory=factory)
    # Private Key: RSA
    factory = RSAPrivateKeyFactory()
    PrivateKey.register(algorithm=AsymmetricKey.RSA, factory=factory)
    PrivateKey.register(algorithm='SHA256withRSA', factory=factory)
    PrivateKey.register(algorithm='RSA/ECB/PKCS1Padding', factory=factory)


__all__ = [

    'PlainKey', 'PlainKeyFactory',
    'AESKey', 'AESKeyFactory',

    'RSAPublicKey', 'RSAPublicKeyFactory',
    'RSAPrivateKey', 'RSAPrivateKeyFactory',

    'ECCPublicKey', 'ECCPublicKeyFactory',
    'ECCPrivateKey', 'ECCPrivateKeyFactory',

    'register_data_digesters',
    'register_symmetric_key_factories',
    'register_asymmetric_key_factories',

]
