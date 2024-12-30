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

from typing import Optional

from dimp import ConstantString
from dimp import sha256, ripemd160
from dimp import base58_encode, base58_decode
from dimp import Address


class BTCAddress(ConstantString, Address):
    """
        Address like BitCoin
        ~~~~~~~~~~~~~~~~~~~~

        data format: "network+digest+code"
            network    --  1 byte
            digest     -- 20 bytes
            check code --  4 bytes

        algorithm:
            fingerprint = PK.data
            digest      = ripemd160(sha256(fingerprint));
            code        = sha256(sha256(network + digest)).prefix(4);
            address     = base58_encode(network + digest + code);
    """

    def __init__(self, address: str, network: int):
        super().__init__(string=address)
        self.__type = network

    @property  # Override
    def network(self) -> int:
        return self.__type

    #
    #   Factory methods
    #
    @classmethod
    def from_data(cls, fingerprint: bytes, network: int) -> Address:
        """
        Generate address with fingerprint and network ID

        :param fingerprint: meta.fingerprint or key.data
        :param network:     address type
        :return: Address object
        """
        # 1. digest = ripemd160(sha256(fingerprint))
        digest = ripemd160(sha256(fingerprint))
        # 2. head = network + digest
        head = chr(network).encode('latin1') + digest
        # 3. cc = sha256(sha256(head)).prefix(4)
        code = check_code(head)
        # 4. data = base58_encode(head + cc)
        address = base58_encode(head + code)
        return cls(address=address, network=network)

    @classmethod
    def from_str(cls, address: str) -> Optional[Address]:
        """
        Parse a string for BTC address

        :param address: address string
        :return: Address object
        """
        if len(address) < 26 or len(address) > 35:
            return None
        # decode
        data = base58_decode(address)
        if data is None or len(data) != 25:
            return None
        # check code
        prefix = data[:21]
        suffix = data[21:]
        if check_code(prefix) == suffix:
            network = ord(data[:1])
            return cls(address=address, network=network)


def check_code(data: bytes) -> bytes:
    # check code in BTC address
    return sha256(sha256(data))[:4]
