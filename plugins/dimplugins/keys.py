# -*- coding: utf-8 -*-
# ==============================================================================
# MIT License
#
# Copyright (c) 2022 Albert Moky
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
from typing import Dict, Any

from mkm.types import Dictionary
from mkm.crypto import CryptographyKey, EncryptKey, SignKey
from mkm.crypto import SymmetricKey, AsymmetricKey
from mkm.crypto import PublicKey, PrivateKey
from mkm.crypto.cryptography import key_algorithm, keys_match
from mkm.crypto.asymmetric import asymmetric_keys_match


class BaseKey(Dictionary, CryptographyKey, ABC):

    def __init__(self, key: Dict[str, Any]):
        super().__init__(dictionary=key)

    @property  # Override
    def algorithm(self) -> str:
        return key_algorithm(key=self.dictionary)


class BaseSymmetricKey(Dictionary, SymmetricKey, ABC):

    def __init__(self, key: Dict[str, Any]):
        super().__init__(dictionary=key)

    # Override
    def __eq__(self, other) -> bool:
        if isinstance(other, SymmetricKey):
            if super().__eq__(other):
                # same dictionary
                return True
            # check by encryption
            return self.match(key=other)

    # Override
    def __ne__(self, other) -> bool:
        if isinstance(other, SymmetricKey):
            if super().__eq__(other):
                # same dictionary
                return False
            # check by encryption
            return not self.match(key=other)
        else:
            return True

    @property  # Override
    def algorithm(self) -> str:
        return key_algorithm(key=self.dictionary)

    # Override
    def match(self, key: EncryptKey) -> bool:
        return keys_match(encrypt_key=key, decrypt_key=self)


class BaseAsymmetricKey(Dictionary, AsymmetricKey, ABC):

    def __init__(self, key: Dict[str, Any]):
        super().__init__(dictionary=key)

    @property  # Override
    def algorithm(self) -> str:
        return key_algorithm(key=self.dictionary)


class BasePublicKey(Dictionary, PublicKey, ABC):

    def __init__(self, key: Dict[str, Any]):
        super().__init__(dictionary=key)

    @property  # Override
    def algorithm(self) -> str:
        return key_algorithm(key=self.dictionary)

    # Override
    def match(self, key: SignKey) -> bool:
        return asymmetric_keys_match(sign_key=key, verify_key=self)


class BasePrivateKey(Dictionary, PrivateKey, ABC):

    def __init__(self, key: Dict[str, Any]):
        super().__init__(dictionary=key)

    # Override
    def __eq__(self, other) -> bool:
        if isinstance(other, PrivateKey):
            if super().__eq__(other):
                # same dictionary
                return True
            # check by signature
            verify_key = self.public_key
            assert verify_key is not None, 'failed to get public key: %s' % self
            return verify_key.match(key=other)

    # Override
    def __ne__(self, other) -> bool:
        if isinstance(other, PrivateKey):
            if super().__eq__(other):
                # same dictionary
                return False
            # check by signature
            verify_key = self.public_key
            assert verify_key is not None, 'failed to get public key: %s' % self
            return not verify_key.match(key=other)
        else:
            return True

    @property  # Override
    def algorithm(self) -> str:
        return key_algorithm(key=self.dictionary)
