# -*- coding: utf-8 -*-
#
#   Dao-Ke-Dao: Universal Message Module
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

from abc import ABC, abstractmethod
from typing import Optional

from dimp import SymmetricKey
from dimp import ID
from dimp import Content
from dimp import InstantMessage
from dimp import EncryptedBundle


class InstantMessageDelegate(ABC):

    """Delegate interface for encrypting InstantMessage to SecureMessage.

    Handles the full encryption pipeline for instant messages, including:
    1. Serialization/encryption of message content (with symmetric key)
    2. Encryption of symmetric key (with receiver's public key)
    """

    #
    #   Encrypt the Instant Message to Secure Message
    #
    #     +----------+      +----------+
    #     | sender   |      | sender   |
    #     | receiver |      | receiver |
    #     | time     |  ->  | time     |
    #     |          |      |          |
    #     | content  |      | data     |  1. data = encrypt(content, PW)
    #     +----------+      | keys     |  2. key  = encrypt(PW, receiver.PK)
    #                       +----------+

    #
    #   Encrypt Content
    #

    @abstractmethod
    async def serialize_content(self, content: Content, password: SymmetricKey, msg: InstantMessage) -> bytes:
        """Serializes message content to raw bytes (Step 1).

        Converts structured Content object to binary format (JSON/Protobuf/etc.),
        using compression algorithm specified in the symmetric key.

        :param content:  message content
        :param password: symmetric key (includes data compression algorithm)
        :param msg:      instant message object
        :return: serialized content data
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.serialize_content()'
        )

    @abstractmethod
    async def encrypt_content(self, data: bytes, password: SymmetricKey, msg: InstantMessage) -> bytes:
        """Encrypts serialized content data with symmetric key (Step 2).

        Uses the symmetric key to encrypt the serialized content data,
        producing the final 'data' field for SecureMessage.

        :param data:     serialized data of message.content
        :param password: symmetric key
        :param msg:      instant message object
        :return: encrypted message content data
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.encrypt_content()'
        )

    # @abstractmethod
    # async def encode_data(self, data: bytes, msg: InstantMessage) -> Any:
    #     """
    #     3. Encode 'message.data' to String (Base64)
    #
    #     :param data:     encrypted content data
    #     :param msg:      instant message object
    #     :return: base64 string
    #     """
    #     raise NotImplementedError(
    #         f'Not implemented: {type(self).__module__}.{type(self).__name__}.encode_data()'
    #     )

    #
    #   Encrypt Key
    #

    @abstractmethod
    async def serialize_key(self, password: SymmetricKey, msg: InstantMessage) -> Optional[bytes]:
        """Serializes symmetric key to raw bytes (Step 4).

        Converts the symmetric key to binary format for encryption. Returns null
        if key is reused (e.g., broadcast messages) or not needed.

        :param password: symmetric key
        :param msg:      instant message object
        :return: serialized key data, None for reused (or broadcast message)
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.serialize_key()'
        )

    @abstractmethod
    async def encrypt_key(self, data: bytes, receiver: ID, msg: InstantMessage) -> Optional[EncryptedBundle]:
        """Encrypts serialized key with receiver's public key (Step 5).

        Uses the receiver's public key (from Visa/Meta) to encrypt the symmetric key,
        producing terminal-specific encrypted data (EncryptedBundle).

        :param data:     serialized data of symmetric key
        :param receiver: actual receiver (user, or group member)
        :param msg:      instant message object
        :return: encrypted key bundle with terminal-specific data
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.encrypt_key()'
        )

    # @abstractmethod
    # async def encode_keys(self, bundle: EncryptedBundle, receiver: ID, msg: InstantMessage) -> StrMap:
    #     """
    #     6. Encode the bundle of encrypted symmetric key data to 'message.keys'
    #
    #     :param bundle:   encrypted key bundle with terminal-specific data
    #     :param receiver: actual receiver (user, or group member)
    #     :param msg:      instant message object
    #     :return: encoded key map (terminal → base64-encoded encrypted key data)
    #     """
    #     raise NotImplementedError(
    #         f'Not implemented: {type(self).__module__}.{type(self).__name__}.encode_keys()'
    #     )
