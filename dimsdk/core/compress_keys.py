# -*- coding: utf-8 -*-
#
#   DIM-SDK : Decentralized Instant Messaging Software Development Kit
#
#                                Written in 2025 by Moky <albert.moky@gmail.com>
#
# ==============================================================================
# MIT License
#
# Copyright (c) 2025 Albert Moky
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

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import List, Tuple, Dict


class Shortener(ABC):
    """ Interface for bidirectional short key mapping (long string keys ↔ single-char keys). """

    #
    #   Compress Content
    #

    @abstractmethod
    def compress_content(self, content: Mapping) -> Mapping:
        """ Shorten keys for content info """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.compress_content()'
        )

    @abstractmethod
    def extract_content(self, content: Mapping) -> Mapping:
        """ Restore keys for content info """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.extract_content()'
        )

    #
    #   Compress SymmetricKey
    #

    @abstractmethod
    def compress_symmetric_key(self, key: Mapping) -> Mapping:
        """ Shorten keys for password info """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.compress_symmetric_key()'
        )

    @abstractmethod
    def extract_symmetric_key(self, key: Mapping) -> Mapping:
        """ Restore keys for password info """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.extract_symmetric_key()'
        )

    #
    #   Compress ReliableMessage
    #

    @abstractmethod
    def compress_reliable_message(self, msg: Mapping) -> Mapping:
        """ Shorten keys for message info """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.compress_reliable_message()'
        )

    @abstractmethod
    def extract_reliable_message(self, msg: Mapping) -> Mapping:
        """ Restore keys for message info """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.extract_reliable_message()'
        )


""" Short Keys

    ======+==================================================+==================
          |   Message        Content        Symmetric Key    |    Description
    ------+--------------------------------------------------+------------------
    "A"   |                                 "algorithm"      |
    "C"   |   "content"      "command"                       |
    "D"   |   "data"                        "data"           |
    "F"   |   "sender"                                       |   (From)
    "G"   |   "group"        "group"                         |
    "I"   |                                 "iv"             |
    "K"   |   "keys"                                         |
    "M"   |   "meta"                                         |
    "N"   |                  "sn"                            |   (Number)
    "P"   |   "visa"                                         |   (Profile)
    "R"   |   "receiver"                                     |
    "S"   |   ...                                            |
    "T"   |   "type"         "type"                          |
    "V"   |   "signature"                                    |   (Verification)
    "W"   |   "time"         "time"                          |   (When)
    ======+==================================================+==================
    
    Note:
        "S" - deprecated (ambiguous for "sender" and "signature")
"""


_message_key_pairs = [
    "F", "sender",      # From
    "R", "receiver",    # Rcpt to
    "W", "time",        # When
    "T", "type",
    "G", "group",
    # ------------------
    "K", "keys",
    "D", "data",
    "V", "signature",   # Verification
    # ------------------
    "M", "meta",
    "P", "visa",        # Profile
]

_content_key_pairs = [
    "T", "type",
    "N", "sn",
    "W", "time",        # When
    "G", "group",
    "C", "command",     # Command name
]

_crypto_key_pairs = [
    "A", "algorithm",
    "D", "data",
    "I", "iv",          # Initial Vector
]


class MessageShortener(Shortener):

    def __init__(self):
        super().__init__()
        # build for content
        c2l, c2s = self._build_content_key_maps()
        self.__content_short_to_long = c2l
        self.__content_long_to_short = c2s
        # build for symmetric key
        k2l, k2s = self._build_crypto_key_maps()
        self.__crypto_short_to_long = k2l
        self.__crypto_long_to_short = k2s
        # build for message
        m2l, m2s = self._build_message_key_maps()
        self.__message_short_to_long = m2l
        self.__message_long_to_short = m2s

    # noinspection PyMethodMayBeStatic
    def _build_content_key_maps(self) -> Tuple[Dict[str, str], Dict[str, str]]:
        return _build(keys=_content_key_pairs)

    # noinspection PyMethodMayBeStatic
    def _build_crypto_key_maps(self) -> Tuple[Dict[str, str], Dict[str, str]]:
        return _build(keys=_crypto_key_pairs)

    # noinspection PyMethodMayBeStatic
    def _build_message_key_maps(self) -> Tuple[Dict[str, str], Dict[str, str]]:
        return _build(keys=_message_key_pairs)

    #
    #   Compress Content
    #

    @property
    def content_short_to_long(self) -> Dict[str, str]:
        return self.__content_short_to_long

    @property
    def content_long_to_short(self) -> Dict[str, str]:
        return self.__content_long_to_short

    # Override
    def compress_content(self, content: Mapping) -> Mapping:
        return _trans(content, dictionary=self.content_long_to_short)

    # Override
    def extract_content(self, content: Mapping) -> Mapping:
        return _trans(content, dictionary=self.content_short_to_long)

    #
    #   Compress SymmetricKey
    #

    @property
    def crypto_short_to_long(self) -> Dict[str, str]:
        return self.__crypto_short_to_long

    @property
    def crypto_long_to_short(self) -> Dict[str, str]:
        return self.__crypto_long_to_short

    # Override
    def compress_symmetric_key(self, key: Mapping) -> Mapping:
        return _trans(key, dictionary=self.crypto_long_to_short)

    # Override
    def extract_symmetric_key(self, key: Mapping) -> Mapping:
        return _trans(key, dictionary=self.crypto_short_to_long)

    #
    #   Compress ReliableMessage
    #

    @property
    def message_short_to_long(self) -> Dict[str, str]:
        return self.__message_short_to_long

    @property
    def message_long_to_short(self) -> Dict[str, str]:
        return self.__message_long_to_short

    # Override
    def compress_reliable_message(self, msg: Mapping) -> Mapping:
        return _trans(msg, dictionary=self.message_long_to_short)

    # Override
    def extract_reliable_message(self, msg: Mapping) -> Mapping:
        return _trans(msg, dictionary=self.message_short_to_long)


def _build(keys: List[str]) -> Tuple[Dict[str, str], Dict[str, str]]:
    """ Build key table """
    short_to_long = {}
    long_to_short = {}
    size = len(keys)
    i = 1
    while i < size:
        k1 = keys[i - 1]
        k2 = keys[i]
        assert len(k1) < len(k2), f'key pair error: {k1}, {k2}'
        short_to_long[k1] = k2
        long_to_short[k2] = k1
        i += 2
    return short_to_long, long_to_short


def _trans(info: Mapping, dictionary: Dict[str, str]) -> Mapping:
    """ Translate """
    result = {}
    for key, value in info.items():
        name = dictionary.get(key)
        if name is None:
            name = key
        result[name] = value
    # OK
    return result
