# -*- coding: utf-8 -*-
#
#   Ming-Ke-Ming : Decentralized User Identity Authentication
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

from abc import ABC
from typing import Optional, Dict

from mkm import Address, AddressFactory
from mkm import ANYWHERE, EVERYWHERE
from mkm import Meta

from dimp.barrack import thanos

from .btc import BTCAddress
from .eth import ETHAddress


"""
    Base Address Factory
    ~~~~~~~~~~~~~~~~~~~~

    abstractmethod:
        - create_address(address)
"""


# noinspection PyAbstractClass
class BaseAddressFactory(AddressFactory, ABC):

    def __init__(self):
        super().__init__()
        self.__addresses: Dict[str, Address] = {}

    # Override
    def generate_address(self, meta: Meta, network: int = None) -> Optional[Address]:
        address = meta.generate_address(network=network)
        assert address is not None, 'failed to generate address with meta: %s' % meta
        self.__addresses[str(address)] = address
        return address

    # Override
    def parse_address(self, address: str) -> Optional[Address]:
        add = self.__addresses.get(address)
        if add is None:
            add = Address.create(address=address)
            if add is not None:
                self.__addresses[address] = add
        return add

    def reduce_memory(self) -> int:
        """
        Call it when received 'UIApplicationDidReceiveMemoryWarningNotification',
        this will remove 50% of cached objects

        :return: number of survivors
        """
        finger = 0
        finger = thanos(self.__addresses, finger)
        return finger >> 1


class GeneralAddressFactory(BaseAddressFactory):

    # Override
    def create_address(self, address: str) -> Optional[Address]:
        size = len(address)
        if size == 8:
            if address.lower() == 'anywhere':
                return ANYWHERE
        elif size == 10:
            if address.lower() == 'everywhere':
                return EVERYWHERE
        res = None
        if size == 42:
            res = ETHAddress.from_str(address=address)
        if 26 <= size <= 35:
            res = BTCAddress.from_str(address=address)
        assert res is not None, 'invalid address: %s' % address
        return res


def register_address_factory():
    Address.register(factory=GeneralAddressFactory())
