# -*- coding: utf-8 -*-
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

import random
from typing import Optional, Any, Dict

from Crypto.Cipher import AES

from mkm.format import base64_decode
from mkm.format import TransportableData
from mkm.crypto import SymmetricKey, SymmetricKeyFactory

from dimp.crypto import BaseSymmetricKey


def random_bytes(size: int) -> bytes:
    # return bytes(numpy.random.bytes(size))
    bits = random.getrandbits(size * 8)
    return bits.to_bytes(length=size, byteorder='little', signed=False)


class AESKey(BaseSymmetricKey):
    """ AES Key """

    def __init__(self, key: Dict[str, Any]):
        super().__init__(key)
        # check key data
        base64 = self.get('data')
        if base64 is None or len(base64) == 0:
            # generate key data & iv
            data, iv = generate(key_size=self.size, block_size=AES.block_size)
            data = TransportableData.create(data=data)
            iv = TransportableData.create(data=iv)
            self.__data = data
            self.__iv = iv
            self['data'] = data.object  # base64_encode()
            self['iv'] = iv.object      # base64_encode()
            # self['mode'] = 'CBC'
            # self['padding'] = 'PKCS7'
        else:
            self.__data: Optional[TransportableData] = None
            self.__iv: Optional[TransportableData] = None

    @property  # Override
    def data(self) -> bytes:
        ted = self.__data
        if ted is None:
            base64 = self.get('data')
            assert len(base64) > 0, 'failed to get key data: %s' % self
            self.__data = ted = TransportableData.parse(base64)
            assert ted is not None, 'key data error: %s' % base64
        return ted.data

    @property
    def iv(self) -> bytes:
        ted = self.__iv
        if ted is None:
            base64 = self.get('iv')
            if base64 is None or len(base64) == 0:
                # iv = b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0'
                iv = AES.block_size * chr(0).encode('utf-8')
            else:
                iv = base64_decode(string=base64)
            self.__iv = ted = TransportableData.create(data=iv)
        return ted.data

    def __set_iv(self, base64: Any):
        # if new iv not exists, this will erase the decoded iv data,
        # and cause reloading from dictionary again.
        self.__iv = TransportableData.parse(base64)

    @property
    def size(self) -> int:
        return self.bits >> 3

    @property
    def bits(self) -> int:
        bits = self.get('sizeInBits')
        if bits is None:
            return 256  # AES-256
        else:
            return int(bits)

    # Override
    def encrypt(self, data: bytes, extra: Optional[Dict]) -> bytes:
        # 0. TODO: random new 'IV'
        if extra is None:
            assert False, 'failed to encrypt without extra info'
        else:
            base64 = self.get_str(key='iv', default=None)
            if base64 is None:
                assert False, 'failed to get initial vector'
            else:
                extra['IV'] = base64
        # 1. get key data & initial vector
        key_data = self.data
        key_iv = self.iv
        # 2. try to encrypt
        data = pkcs7_pad(data=data, block_size=AES.block_size)
        key = AES.new(key_data, AES.MODE_CBC, key_iv)
        return key.encrypt(data)

    # Override
    def decrypt(self, data: bytes, params: Optional[Dict]) -> Optional[bytes]:
        # 0. get 'IV' from extra params
        if params is None:
            assert False, 'failed to decrypt without extra params'
        else:
            base64 = params.get('IV')
            if base64 is not None:
                self.__set_iv(base64=base64)
        # 1. get key data & initial vector
        key_data = self.data
        key_iv = self.iv
        # 2. try to decrypt
        try:
            key = AES.new(key_data, AES.MODE_CBC, key_iv)
            plaintext = key.decrypt(data)
            return pkcs7_unpad(data=plaintext)
        except ValueError:
            return None


def generate(key_size: int, block_size: int) -> (bytes, bytes):
    data = random_bytes(key_size)
    iv = random_bytes(block_size)
    return data, iv


def pkcs7_pad(data: bytes, block_size: int) -> bytes:
    assert data is not None, 'data cannot be None'
    amount = block_size - len(data) % block_size
    if amount == 0:
        amount = block_size
    pad = chr(amount).encode('utf-8')
    return data + pad * amount


def pkcs7_unpad(data: bytes) -> bytes:
    assert data is not None and len(data) > 0, 'data empty'
    amount = data[-1]
    assert len(data) >= amount
    return data[:-amount]


"""
    Key Factory
    ~~~~~~~~~~~
"""


class AESKeyFactory(SymmetricKeyFactory):

    # Override
    def generate_symmetric_key(self) -> Optional[SymmetricKey]:
        key = {'algorithm': SymmetricKey.AES}
        return AESKey(key)

    # Override
    def parse_symmetric_key(self, key: dict) -> Optional[SymmetricKey]:
        return AESKey(key)
