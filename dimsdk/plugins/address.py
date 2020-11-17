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

from dimp import Hex
from dimp import Address, NetworkID

from .digest import keccak256


# https://eips.ethereum.org/EIPS/eip-55
def eip55(address: str) -> str:
    res = ''
    table = keccak256(address.encode('utf-8'))
    for i in range(40):
        ch = address[i]
        x = ord(ch)
        if x > 0x39:
            # check for each 4 bits in the hash table
            # if the first bit is '1',
            #     change the character to uppercase
            x -= (table[i >> 1] << (i << 2 & 4) & 0x80) >> 2
            ch = chr(x)
        res += ch
    return res


"""
    Address like Ethereum
    ~~~~~~~~~~~~~~~~~~~~~

    data format: "0x{address}"

    algorithm:
        fingerprint = PK.data
        digest      = keccak256(fingerprint)
        address     = hex_encode(digest.suffix(20))
"""


class ETHAddress(str, Address):

    def __new__(cls, address: str):
        if not address.startswith('0x'):
            raise ValueError('Not an ETH address: %s' % address)
        return super().__new__(cls, address)

    def __init__(self, address: str):
        if self is address:
            # no need to init again
            return
        super().__init__()

    @property
    def network(self) -> int:
        return NetworkID.Main.value

    @property
    def number(self) -> int:
        return 9527

    #
    #   Factory
    #
    @classmethod
    def new(cls, data: bytes) -> Address:
        """
        Generate address with key data

        :param data:    key.data
        :return:        Address object
        """
        if len(data) == 65:
            data = data[1:]
        assert len(data) == 64, 'key data length error: %d' % len(data)
        # 1. digest = keccak256(fingerprint)
        digest = keccak256(data)
        # 2. address = hex_encode(digest.suffix(20))
        tail = digest[-20:]
        address = '0x' + eip55(Hex.encode(tail))
        return cls(address)

    @staticmethod
    def validate_address(address: str) -> str:
        address = address.lower()
        if address.startswith('0x'):
            address = address[2:]
        return '0x' + eip55(address)

    @staticmethod
    def is_validate(address: str) -> bool:
        length = len(address)
        if length != 42:
            return False
        if address[0] != '0' or address[1] != 'x':
            return False
        for i in range(2, 42):
            ch = address[i]
            if '0' <= ch <= '9':
                continue
            if 'A' <= ch <= 'Z':
                continue
            if 'a' <= ch <= 'z':
                continue
            # unexpected character
            return False
        sub = address[2:]
        return eip55(sub.lower()) == sub


# register ETH address class
Address.register(ETHAddress)
