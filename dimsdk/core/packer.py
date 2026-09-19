# -*- coding: utf-8 -*-
#
#   DIM-SDK : Decentralized Instant Messaging Software Development Kit
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

from abc import ABC, abstractmethod
from typing import Optional

from dimp import InstantMessage, SecureMessage, ReliableMessage


class Packer(ABC):
    """Message packing/unpacking interface (encryption → signature → serialization).

    Core workflow (packing):
    `InstantMessage` (plain) → `SecureMessage` (encrypted) → `ReliableMessage` (signed) → `Uint8List` (binary)

    Core workflow (unpacking):
    `Uint8List` (binary) → `ReliableMessage` (signed) → `SecureMessage` (encrypted) → `InstantMessage` (plain)
    """

    #
    #   InstantMessage -> SecureMessage -> ReliableMessage -> Data
    #

    @abstractmethod
    async def encrypt_message(self, msg: InstantMessage) -> Optional[SecureMessage]:
        """
        Encrypts the content of a plain instant message to create a secure message.

        :param msg: plain message
        :return: encrypted message
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.encrypt_message()'
        )

    @abstractmethod
    async def sign_message(self, msg: SecureMessage) -> Optional[ReliableMessage]:
        """
        Signs the encrypted data of a secure message to create a reliable message.

        :param msg: encrypted message
        :return: network message
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.sign_message()'
        )

    # @abstractmethod
    # async def serialize_message(self, msg: ReliableMessage) -> Optional[bytes]:
    #     """
    #     Serialize network message
    #
    #     :param msg: network message
    #     :return: data package
    #     """
    #     raise NotImplementedError(
    #         f'Not implemented: {type(self).__module__}.{type(self).__name__}.serialize_message()'
    #     )

    #
    #   Data -> ReliableMessage -> SecureMessage -> InstantMessage
    #

    # @abstractmethod
    # async def deserialize_message(self, data: bytes) -> Optional[ReliableMessage]:
    #     """
    #     Deserialize network message
    #
    #     :param data: data package
    #     :return: network message
    #     """
    #     raise NotImplementedError(
    #         f'Not implemented: {type(self).__module__}.{type(self).__name__}.deserialize_message()'
    #     )

    @abstractmethod
    async def verify_message(self, msg: ReliableMessage) -> Optional[SecureMessage]:
        """
        Verifies the signature of a reliable message to retrieve the secure message.

        :param msg: network message
        :return: encrypted message
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.verify_message()'
        )

    @abstractmethod
    async def decrypt_message(self, msg: SecureMessage) -> Optional[InstantMessage]:
        """
        Decrypts the data of a secure message to retrieve the plain instant message.

        :param msg: encrypted message
        :return: plain message
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.decrypt_message()'
        )
