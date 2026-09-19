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
from typing import List, Tuple

from dimp import StrMap


"""
    Generic for Keys Map
    ~~~~~~~~~~~~~~~~~~~~
"""
try:
    import collections.abc as abc
    StringPairing = abc.Mapping[str, str]
except TypeError:
    import typing
    StringPairing = typing.Mapping[str, str]


class Shortener(ABC):
    """Interface for bidirectional short key mapping (long string keys ↔ single-char keys).

    Core function: Replace system-defined long string keys with pre-defined single-character
    short keys (and vice versa) to reduce the size of JSON-serialized data.

    Key features:
    - Bi-directional conversion (compress → extract)
    - Preserves data structure, only replaces key names
    - Maintains compatibility with core message components
    """

    #
    #   Compress Content
    #

    @abstractmethod
    def compress_content(self, content: StrMap) -> StrMap:
        """ Shorten keys for content info """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.compress_content()'
        )

    @abstractmethod
    def extract_content(self, content: StrMap) -> StrMap:
        """ Restore keys for content info """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.extract_content()'
        )

    #
    #   Compress SymmetricKey
    #

    @abstractmethod
    def compress_symmetric_key(self, key: StrMap) -> StrMap:
        """ Shorten keys for password info """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.compress_symmetric_key()'
        )

    @abstractmethod
    def extract_symmetric_key(self, key: StrMap) -> StrMap:
        """ Restore keys for password info """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.extract_symmetric_key()'
        )

    #
    #   Compress ReliableMessage
    #

    @abstractmethod
    def compress_reliable_message(self, msg: StrMap) -> StrMap:
        """ Shorten keys for message info """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.compress_reliable_message()'
        )

    @abstractmethod
    def extract_reliable_message(self, msg: StrMap) -> StrMap:
        """ Restore keys for message info """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.extract_reliable_message()'
        )

    #
    #   Short Keys
    #

    # Compress ReliableMessage
    message_short_keys = [
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

    # Compress Content
    content_short_keys = [
        "T", "type",
        "N", "sn",
        "W", "time",        # When
        "G", "group",
        "C", "command",     # Command name
    ]

    # Compress SymmetricKey
    crypto_short_keys = [
        "A", "algorithm",
        "D", "data",
        "I", "iv",          # Initial Vector
    ]


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


class MessageShortener(Shortener):
    """Concrete implementation of :class:`Shortener` for message/content/key short key mapping.

    Implements fixed key pair conversion with new Map creation
    (does not modify the original one).
    """

    def __init__(self):
        super().__init__()

        # build for message
        m2l, m2s = self._build_message_key_maps()
        self.__message_short_to_long = m2l
        self.__message_long_to_short = m2s

        # build for content
        c2l, c2s = self._build_content_key_maps()
        self.__content_short_to_long = c2l
        self.__content_long_to_short = c2s

        # build for symmetric key
        k2l, k2s = self._build_crypto_key_maps()
        self.__crypto_short_to_long = k2l
        self.__crypto_long_to_short = k2s

    # protected
    def _build_message_key_maps(self) -> Tuple[StringPairing, StringPairing]:
        """Builds the short-to-long and long-to-short maps for message keys.

        Uses the standard message key pairs defined in
        :attr:`~Shortener.message_short_keys`.

        Returns a record of (shortToLong, longToShort) mapping tables.
        """
        return self._build(keys=self.message_short_keys)

    # protected
    def _build_content_key_maps(self) -> Tuple[StringPairing, StringPairing]:
        """Builds the short-to-long and long-to-short maps for content keys.

        Uses the standard content key pairs defined in
        :attr:`~Shortener.content_short_keys`.

        Returns a record of (shortToLong, longToShort) mapping tables.
        """
        return self._build(keys=self.content_short_keys)

    # protected
    def _build_crypto_key_maps(self) -> Tuple[StringPairing, StringPairing]:
        """Builds the short-to-long and long-to-short maps for symmetric key fields.

        Uses the standard crypto key pairs defined in
        :attr:`~Shortener.crypto_short_keys`.

        Returns a record of (shortToLong, longToShort) mapping tables.
        """
        return self._build(keys=self.crypto_short_keys)

    # protected
    # noinspection PyMethodMayBeStatic
    def _build(self, keys: List[str]) -> Tuple[StringPairing, StringPairing]:
        """Builds two mapping tables from a list of (shortKey, longKey) pairs.

        The ``keys`` list must contain pairs in order: short key followed by long key.

        :param keys: flattened list of (short, long) key pairs
        :return: record of (shortToLong, longToShort) mapping tables
        """
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

    # protected
    # noinspection PyMethodMayBeStatic
    def _translate(self, info: StrMap, dictionary: StringPairing) -> StrMap:
        """Translates the keys of ``info`` using the given ``dictionary``.

        NOTICE: does not modify the original map, creates a new one instead.

        :param info: source map whose keys need translation
        :param dictionary: mapping table (old key -> new key)
        :return: new map with translated keys (unmatched keys kept as-is)
        """
        result = {}
        for key, value in info.items():
            name = dictionary.get(key)
            if name is None:
                name = key
            result[name] = value
        # OK
        return result

    # -------------------------------------------------------------------------
    #  ReliableMessage Key Mapping
    # -------------------------------------------------------------------------

    @property
    def message_short_to_long(self) -> StringPairing:
        return self.__message_short_to_long

    @property
    def message_long_to_short(self) -> StringPairing:
        return self.__message_long_to_short

    # Override
    def compress_reliable_message(self, msg: StrMap) -> StrMap:
        return self._translate(info=msg, dictionary=self.message_long_to_short)

    # Override
    def extract_reliable_message(self, msg: StrMap) -> StrMap:
        return self._translate(info=msg, dictionary=self.message_short_to_long)

    # -------------------------------------------------------------------------
    #  Content Key Mapping
    # -------------------------------------------------------------------------

    @property
    def content_short_to_long(self) -> StringPairing:
        return self.__content_short_to_long

    @property
    def content_long_to_short(self) -> StringPairing:
        return self.__content_long_to_short

    # Override
    def compress_content(self, content: StrMap) -> StrMap:
        return self._translate(info=content, dictionary=self.content_long_to_short)

    # Override
    def extract_content(self, content: StrMap) -> StrMap:
        return self._translate(info=content, dictionary=self.content_short_to_long)

    # -------------------------------------------------------------------------
    #  Symmetric Key Mapping
    # -------------------------------------------------------------------------

    @property
    def crypto_short_to_long(self) -> StringPairing:
        return self.__crypto_short_to_long

    @property
    def crypto_long_to_short(self) -> StringPairing:
        return self.__crypto_long_to_short

    # Override
    def compress_symmetric_key(self, key: StrMap) -> StrMap:
        return self._translate(info=key, dictionary=self.crypto_long_to_short)

    # Override
    def extract_symmetric_key(self, key: StrMap) -> StrMap:
        return self._translate(info=key, dictionary=self.crypto_short_to_long)
