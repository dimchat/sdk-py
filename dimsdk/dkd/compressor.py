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
from typing import Optional

from dimp import StrMap
from dimp import JSONMap
from dimp import UTF8

from .compress_keys import Shortener


# -----------------------------------------------------------------------------
#  Compressor (Short Key + JSON + UTF8 Encoding)
# -----------------------------------------------------------------------------

class Compressor(ABC):
    """ Interface for message data compression (short key mapping + JSON serialization + UTF8 encoding).

        Core workflow:
        1. Shorten keys via Shortener
        2. Serialize to JSON string
        3. Encode to UTF8 binary bytes

        Extraction workflow (reverse):
        1. Decode UTF8 bytes to JSON string
        2. Deserialize to Map
        3. Restore long keys via Shortener
    """

    # -------------------------------------------------------------------------
    #  Content Compression/Extraction
    # -------------------------------------------------------------------------

    @abstractmethod
    def compress_content(self, content: StrMap, key: StrMap) -> bytes:
        """ Compress content info """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.compress_content()'
        )

    @abstractmethod
    def extract_content(self, data: bytes, key: StrMap) -> Optional[StrMap]:
        """ Extract content info """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.extract_content()'
        )

    # -------------------------------------------------------------------------
    #  Symmetric Key Compression/Extraction
    # -------------------------------------------------------------------------

    @abstractmethod
    def compress_symmetric_key(self, key: StrMap) -> bytes:
        """ Compress password info """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.compress_symmetric_key()'
        )

    @abstractmethod
    def extract_symmetric_key(self, data: bytes) -> Optional[StrMap]:
        """ Extract password info """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.extract_symmetric_key()'
        )

    # -------------------------------------------------------------------------
    #  ReliableMessage Compression/Extraction
    # -------------------------------------------------------------------------

    @abstractmethod
    def compress_reliable_message(self, msg: StrMap) -> bytes:
        """ Compress message info """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.compress_reliable_message()'
        )

    @abstractmethod
    def extract_reliable_message(self, data: bytes) -> Optional[StrMap]:
        """ Extract message info """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.extract_reliable_message()'
        )


class MessageCompressor(Compressor):
    """ Concrete implementation of Compressor (Shortener + JSON + UTF8).

        Uses MessageShortener for key mapping, JSON for serialization,
        and UTF8 for binary encoding/decoding.
    """

    def __init__(self, shortener: Shortener):
        super().__init__()
        self.__shortener = shortener

    @property  # protected
    def shortener(self) -> Shortener:
        return self.__shortener

    # -------------------------------------------------------------------------
    #  Content Compression/Extraction
    # -------------------------------------------------------------------------

    # Override
    def compress_content(self, content: StrMap, key: StrMap) -> bytes:
        content = self.shortener.compress_content(content=content)
        json = JSONMap.encode(container=content)
        return UTF8.encode(string=json)

    # Override
    def extract_content(self, data: bytes, key: StrMap) -> Optional[StrMap]:
        json = UTF8.decode(data=data)
        if json is None:
            # assert False, f'content data error: {len(data)}'
            return None
        info = JSONMap.decode(string=json)
        if info is None:
            # assert False, f'failed to decode content: {json}'
            return None
        return self.shortener.extract_content(content=info)

    # -------------------------------------------------------------------------
    #  Symmetric Key Compression/Extraction
    # -------------------------------------------------------------------------

    # Override
    def compress_symmetric_key(self, key: StrMap) -> bytes:
        key = self.shortener.compress_symmetric_key(key=key)
        json = JSONMap.encode(container=key)
        return UTF8.encode(string=json)

    # Override
    def extract_symmetric_key(self, data: bytes) -> Optional[StrMap]:
        json = UTF8.decode(data=data)
        if json is None:
            # assert False, f'symmetric key data error: {len(data)}'
            return None
        key = JSONMap.decode(string=json)
        if key is None:
            # assert False, f'failed to decode symmetric key: {json}'
            return None
        return self.shortener.extract_symmetric_key(key=key)

    # -------------------------------------------------------------------------
    #  ReliableMessage Compression/Extraction
    # -------------------------------------------------------------------------

    # Override
    def compress_reliable_message(self, msg: StrMap) -> bytes:
        msg = self.shortener.compress_reliable_message(msg=msg)
        json = JSONMap.encode(container=msg)
        return UTF8.encode(string=json)

    # Override
    def extract_reliable_message(self, data: bytes) -> Optional[StrMap]:
        json = UTF8.decode(data=data)
        if json is None:
            # assert False, f'message data error: {len(data)}'
            return None
        msg = JSONMap.decode(string=json)
        if msg is None:
            # assert False, f'failed to decode message: {json}'
            return None
        return self.shortener.extract_reliable_message(msg=msg)
