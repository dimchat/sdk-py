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

from typing import Union, Optional

from mkm.crypto import VerifyKey

from dimp import EntityType, Address
from dimp import MetaType, BaseMeta

from .btc import BTCAddress, NetworkType
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

    def __init__(self, meta: Optional[dict] = None,
                 version: Union[MetaType, int] = 0, key: Optional[VerifyKey] = None,
                 seed: Optional[str] = None, fingerprint: Union[bytes, str, None] = None):
        super().__init__(meta=meta, version=version, key=key, seed=seed, fingerprint=fingerprint)
        # caches
        self.__addresses = {}

    # Override
    def generate_address(self, network: Union[EntityType, NetworkType, int]) -> Address:
        assert self.type == MetaType.MKM, 'meta version error: %d' % self.type
        if isinstance(network, EntityType):
            network = network.value
        elif isinstance(network, NetworkType):
            network = network.value
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

    def __init__(self, meta: Optional[dict] = None,
                 version: Union[MetaType, int] = 0, key: Optional[VerifyKey] = None,
                 seed: Optional[str] = None, fingerprint: Union[bytes, str, None] = None):
        super().__init__(meta=meta, version=version, key=key, seed=seed, fingerprint=fingerprint)
        # caches
        self.__address: Optional[Address] = None

    # Override
    def generate_address(self, network: Union[EntityType, int]) -> Address:
        assert self.type in [MetaType.BTC, MetaType.ExBTC], 'meta version error: %d' % self.type
        # assert network == NetworkType.BTC_MAIN, 'BTC address type error: %d' % network
        if self.__address is None:
            # generate and cache it
            data = self.key.data
            self.__address = BTCAddress.from_data(data, network=network)
        return self.__address


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

    def __init__(self, meta: Optional[dict] = None,
                 version: Union[MetaType, int] = 0, key: Optional[VerifyKey] = None,
                 seed: Optional[str] = None, fingerprint: Union[bytes, str, None] = None):
        super().__init__(meta=meta, version=version, key=key, seed=seed, fingerprint=fingerprint)
        # caches
        self.__address: Optional[Address] = None

    # Override
    def generate_address(self, network: Union[EntityType, int]) -> Address:
        assert self.type in [MetaType.ETH, MetaType.ExETH], 'meta version error: %d' % self.type
        assert network == EntityType.USER, 'ETH address type error: %d' % network
        if self.__address is None:
            # generate and cache it
            data = self.key.data
            self.__address = ETHAddress.from_data(data)
        return self.__address
