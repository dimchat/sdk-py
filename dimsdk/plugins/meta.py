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

from typing import Union

from dimp import ID, NetworkID, Address, MetaVersion, Meta

from .address import ETHAddress


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


class ETHMeta(Meta):

    def __init__(self, meta: dict):
        if self is meta:
            # no need to init again
            return
        super().__init__(meta)
        # id caches
        self.__id: ID = None
        self.__address: Address = None

    def generate_identifier(self, network: Union[NetworkID, int]) -> ID:
        if self.__id is None:
            address = self.generate_address(network=network)
            self.__id = ID.new(name=self.seed, address=address)
        return self.__id

    def generate_address(self, network: int) -> Address:
        assert self.version in [MetaVersion.ETH.value, MetaVersion.ExETH.value], 'meta version error: %d' % self.version
        assert self.valid, 'meta not valid: %s' % self
        if self.__address is None:
            self.__address = ETHAddress.new(data=self.key.data)
        return self.__address


# register meta class with version
Meta.register(version=MetaVersion.ETH, meta_class=ETHMeta)
Meta.register(version=MetaVersion.ExETH, meta_class=ETHMeta)
