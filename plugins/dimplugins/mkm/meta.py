# -*- coding: utf-8 -*-
#
#   Ming-Ke-Ming : Decentralized User Identity Authentication
#
#                                Written in 2020 by Moky <albert.moky@gmail.com>
#
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

from typing import Union, Optional, Any, Dict

from mkm.format import utf8_encode
from mkm.format import TransportableData
from mkm.crypto import VerifyKey, SignKey, PrivateKey
from mkm import EntityType, Address
from mkm import MetaType, Meta, MetaFactory
from mkm import AccountFactoryManager

from dimp.mkm import BaseMeta

from .btc import BTCAddress
from .eth import ETHAddress


"""
    Default Meta to build ID with 'name@address'
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    version:
        0x01 - MKM

    algorithm:
        CT      = fingerprint = sKey.sign(seed);
        hash    = ripemd160(sha256(CT));
        code    = sha256(sha256(network + hash)).prefix(4);
        address = base58_encode(network + hash + code);
"""


class DefaultMeta(BaseMeta):

    def __init__(self, meta: Dict[str, Any] = None,
                 version: int = None, key: VerifyKey = None,
                 seed: Optional[str] = None, fingerprint: Optional[TransportableData] = None):
        super().__init__(meta=meta, version=version, key=key, seed=seed, fingerprint=fingerprint)
        # caches
        self.__addresses = {}

    # Override
    def generate_address(self, network: int = None) -> Address:
        assert self.type == MetaType.MKM, 'meta version error: %d' % self.type
        assert network is not None, 'address type should not be empty'
        # check caches
        address = self.__addresses.get(network)
        if address is None:
            # generate and cache it
            data = self.fingerprint
            address = BTCAddress.from_data(data, network=network)
            self.__addresses[network] = address
        return address


"""
    Meta to build BTC address for ID
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    version:
        0x02 - BTC
        0x03 - ExBTC

    algorithm:
        CT      = key.data;
        hash    = ripemd160(sha256(CT));
        code    = sha256(sha256(network + hash)).prefix(4);
        address = base58_encode(network + hash + code);
"""


class BTCMeta(BaseMeta):

    def __init__(self, meta: Dict[str, Any] = None,
                 version: int = None, key: VerifyKey = None,
                 seed: Optional[str] = None, fingerprint: Optional[TransportableData] = None):
        super().__init__(meta=meta, version=version, key=key, seed=seed, fingerprint=fingerprint)
        # caches
        self.__address: Optional[Address] = None

    # Override
    def generate_address(self, network: int = None) -> Address:
        assert self.type in [MetaType.BTC, MetaType.ExBTC], 'meta version error: %d' % self.type
        cached = self.__address
        if cached is None or cached.type != network:
            # TODO: compress public key?
            key = self.public_key
            data = key.data
            # generate and cache it
            self.__address = cached = BTCAddress.from_data(data, network=network)
        return cached


"""
    Meta to build ETH address for ID
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    version:
        0x04 - ETH
        0x05 - ExETH

    algorithm:
        fingerprint = key.data
        digest      = keccak256(fingerprint)
        address     = hex_encode(digest.suffix(20))
"""


class ETHMeta(BaseMeta):

    def __init__(self, meta: Dict[str, Any] = None,
                 version: int = None, key: VerifyKey = None,
                 seed: Optional[str] = None, fingerprint: Optional[TransportableData] = None):
        super().__init__(meta=meta, version=version, key=key, seed=seed, fingerprint=fingerprint)
        # caches
        self.__address: Optional[Address] = None

    # Override
    def generate_address(self, network: int = None) -> Address:
        assert self.type in [MetaType.ETH, MetaType.ExETH], 'meta version error: %d' % self.type
        assert network == EntityType.USER, 'ETH address type error: %d' % network
        cached = self.__address
        if cached is None:  # or cached.type != network:
            # 64 bytes key data without prefix 0x04
            key = self.public_key
            data = key.data
            # generate and cache it
            self.__address = cached = ETHAddress.from_data(data)
        return cached


class GeneralMetaFactory(MetaFactory):

    def __init__(self, version: Union[int, MetaType]):
        super().__init__()
        if isinstance(version, MetaType):
            version = version.value
        self.__type = version

    # Override
    def generate_meta(self, key: SignKey, seed: Optional[str]) -> Meta:
        if seed is None or len(seed) == 0:
            fingerprint = None
        else:
            sig = key.sign(data=utf8_encode(string=seed))
            fingerprint = TransportableData.create(data=sig)
        assert isinstance(key, PrivateKey), 'private key error: %s' % key
        public_key = key.public_key
        return self.create_meta(key=public_key, seed=seed, fingerprint=fingerprint)

    # Override
    def create_meta(self, key: VerifyKey, seed: Optional[str], fingerprint: Optional[TransportableData]) -> Meta:
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
        gf = AccountFactoryManager.general_factory
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
        if out.valid:
            return out


def register_meta_factories():
    Meta.register(version=MetaType.MKM, factory=GeneralMetaFactory(version=MetaType.MKM))
    Meta.register(version=MetaType.BTC, factory=GeneralMetaFactory(version=MetaType.BTC))
    Meta.register(version=MetaType.ExBTC, factory=GeneralMetaFactory(version=MetaType.ExBTC))
    Meta.register(version=MetaType.ETH, factory=GeneralMetaFactory(version=MetaType.ETH))
    Meta.register(version=MetaType.ExETH, factory=GeneralMetaFactory(version=MetaType.ExETH))
