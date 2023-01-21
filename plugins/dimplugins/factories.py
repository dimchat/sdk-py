# -*- coding: utf-8 -*-
# ==============================================================================
# MIT License
#
# Copyright (c) 2020 Albert Moky
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

from typing import Optional, Union

from mkm.crypto import utf8_encode
from mkm.crypto import SymmetricKey, AsymmetricKey
from mkm.crypto import SignKey, VerifyKey
from mkm.crypto import PublicKey, PrivateKey
from mkm.crypto import SymmetricKeyFactory, PublicKeyFactory, PrivateKeyFactory
from mkm.factory import FactoryManager

from mkm import ANYWHERE, EVERYWHERE, Address
from mkm import MetaType, Meta, MetaFactory

from dimp import BaseAddressFactory

from .rsa import RSAPublicKey, RSAPrivateKey
from .ecc import ECCPublicKey, ECCPrivateKey
from .aes import AESKey
from .plain import PlainKey
from .btc import BTCAddress
from .eth import ETHAddress
from .meta import DefaultMeta, BTCMeta, ETHMeta


class RSAPublicKeyFactory(PublicKeyFactory):

    # Override
    def parse_public_key(self, key: dict) -> Optional[PublicKey]:
        return RSAPublicKey(key=key)


class ECCPublicKeyFactory(PublicKeyFactory):

    # Override
    def parse_public_key(self, key: dict) -> Optional[PublicKey]:
        return ECCPublicKey(key=key)


class RSAPrivateKeyFactory(PrivateKeyFactory):

    # Override
    def generate_private_key(self) -> Optional[PrivateKey]:
        key = {'algorithm': AsymmetricKey.RSA}
        return RSAPrivateKey(key=key)

    # Override
    def parse_private_key(self, key: dict) -> Optional[PrivateKey]:
        return RSAPrivateKey(key=key)


class ECCPrivateKeyFactory(PrivateKeyFactory):

    # Override
    def generate_private_key(self) -> Optional[PrivateKey]:
        key = {'algorithm': AsymmetricKey.ECC}
        return ECCPrivateKey(key=key)

    # Override
    def parse_private_key(self, key: dict) -> Optional[PrivateKey]:
        return ECCPrivateKey(key=key)


class AESKeyFactory(SymmetricKeyFactory):

    # Override
    def generate_symmetric_key(self) -> Optional[SymmetricKey]:
        key = {'algorithm': SymmetricKey.AES}
        return AESKey(key=key)

    # Override
    def parse_symmetric_key(self, key: dict) -> Optional[SymmetricKey]:
        return AESKey(key=key)


class PlainKeyFactory(SymmetricKeyFactory):

    def __init__(self):
        super().__init__()
        self.__plain_key = PlainKey()

    # Override
    def generate_symmetric_key(self) -> Optional[SymmetricKey]:
        return self.__plain_key

    # Override
    def parse_symmetric_key(self, key: dict) -> Optional[SymmetricKey]:
        return self.__plain_key


class GeneralAddressFactory(BaseAddressFactory):

    # Override
    def create_address(self, address: str) -> Optional[Address]:
        size = len(address)
        if size == 8 and address.lower() == 'anywhere':
            return ANYWHERE
        if size == 10 and address.lower() == 'everywhere':
            return EVERYWHERE
        if size == 42:
            return ETHAddress.from_str(address=address)
        if 26 <= size <= 35:
            return BTCAddress.from_str(address=address)


class GeneralMetaFactory(MetaFactory):

    def __init__(self, version: Union[MetaType, int]):
        super().__init__()
        self.__type = version

    # Override
    def generate_meta(self, key: SignKey, seed: Optional[str]) -> Meta:
        if seed is None or len(seed) == 0:
            fingerprint = None
        else:
            fingerprint = key.sign(data=utf8_encode(string=seed))
        assert isinstance(key, PrivateKey), 'private key error: %s' % key
        return self.create_meta(key=key.public_key, seed=seed, fingerprint=fingerprint)

    # Override
    def create_meta(self, key: VerifyKey, seed: Optional[str], fingerprint: Optional[bytes]) -> Meta:
        if self.__type == MetaType.MKM:
            # MKM
            return DefaultMeta(version=self.__type, key=key, seed=seed, fingerprint=fingerprint)
        elif self.__type == MetaType.BTC:
            # BTC
            return BTCMeta(version=self.__type, key=key)
        elif self.__type == MetaType.ExBTC:
            # ExBTC
            return BTCMeta(version=self.__type, key=key, seed=seed, fingerprint=fingerprint)
        elif self.__type == MetaType.ETH:
            # ETH
            return ETHMeta(version=self.__type, key=key)
        elif self.__type == MetaType.ExETH:
            # ExETH
            return ETHMeta(version=self.__type, key=key, seed=seed, fingerprint=fingerprint)

    # Override
    def parse_meta(self, meta: dict) -> Optional[Meta]:
        gf = FactoryManager.general_factory
        version = gf.get_meta_type(meta=meta)
        if version == MetaType.MKM:
            # MKM
            out = DefaultMeta(meta=meta)
        elif version == MetaType.BTC or version == MetaType.ExBTC:
            # BTC, ExBTC
            out = BTCMeta(meta=meta)
        elif version == MetaType.ETH or version == MetaType.ExETH:
            # ETH, ExETH
            out = ETHMeta(meta=meta)
        else:
            raise TypeError('unknown meta type: %d' % version)
        if Meta.check(meta=out):
            return out
