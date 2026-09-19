# -*- coding: utf-8 -*-
#
#   DIM-SDK : Decentralized Instant Messaging Software Development Kit
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

"""
    Messenger
    ~~~~~~~~~

    Transform and send message
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from dimp import SymmetricKey
from dimp import Content
from dimp import InstantMessage, SecureMessage, ReliableMessage

from ..core import Transformer, Packer, Processor
from ..core import CipherKeyDelegate


class Messenger(Transformer, Packer, Processor, ABC):
    """Unified messaging service (combines packing, processing, and key management).

    Acts as a facade for all messaging operations:
    1. Delegates packing/unpacking to a :class:`Packer` implementation
    2. Delegates message processing to a :class:`Processor` implementation
    3. Manages directional symmetric keys via :class:`CipherKeyDelegate`

    Implements: :class:`Transformer`, :class:`Packer`, :class:`Processor`
    """

    @property  # protected
    @abstractmethod
    def cipher_key_delegate(self) -> Optional[CipherKeyDelegate]:
        """Key management delegate (directional symmetric keys) - internal use only."""
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.cipher_key_delegate getter'
        )

    @property  # protected
    @abstractmethod
    def packer(self) -> Optional[Packer]:
        """Message packer implementation (delegated packing/unpacking) - internal use only."""
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.packer getter'
        )

    @property  # protected
    @abstractmethod
    def processor(self) -> Optional[Processor]:
        """Message processor implementation (delegated processing) - internal use only."""
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.processor getter'
        )

    #
    #   SecureMessageDelegate
    #

    # Override
    async def deserialize_key(self, data: Optional[bytes], msg: SecureMessage) -> Optional[SymmetricKey]:
        if data is None:
            # get key from cache with direction: sender -> receiver(group)
            return await self.get_decrypt_key(msg=msg)
        # cache decrypt key when success
        password = await super().deserialize_key(data=data, msg=msg)
        if password is not None:
            # cache the key with direction: sender -> receiver(group)
            await self.cache_decrypt_key(key=password, msg=msg)
        return password

    #
    #   Interfaces for Cipher Key
    #

    async def get_encrypt_key(self, msg: InstantMessage) -> Optional[SymmetricKey]:
        """Retrieves the encryption key for an instant message (generates if missing).

        Uses directional key scoping (sender -> target) via :class:`CipherKeyDelegate`.

        `msg` is the instant message to get encryption key for.

        Returns the directional symmetric encryption key (None if unavailable).
        """
        sender = msg.sender
        target = CipherKeyDelegate.destination_for_message(msg=msg)
        db = self.cipher_key_delegate
        return await db.get_cipher_key(sender=sender, receiver=target, generate=True)

    async def get_decrypt_key(self, msg: SecureMessage) -> Optional[SymmetricKey]:
        """Retrieves the decryption key for a secure message (does not generate).

        Uses directional key scoping (sender -> target) via :class:`CipherKeyDelegate`.

        `msg` is the secure message to get decryption key for.

        Returns the directional symmetric decryption key (None if unavailable).
        """
        sender = msg.sender
        target = CipherKeyDelegate.destination_for_message(msg=msg)
        db = self.cipher_key_delegate
        return await db.get_cipher_key(sender=sender, receiver=target, generate=False)

    async def cache_decrypt_key(self, key: SymmetricKey, msg: SecureMessage):
        """Caches a decryption key for future use (directional scoping).

        `key` is the symmetric key to cache.
        `msg` is the secure message (for direction context).

        Returns a future that completes when caching is done (no return value).
        """
        sender = msg.sender
        target = CipherKeyDelegate.destination_for_message(msg=msg)
        db = self.cipher_key_delegate
        return await db.cache_cipher_key(key=key, sender=sender, receiver=target)

    #
    #   Interfaces for Packing Message
    #

    # Override
    async def encrypt_message(self, msg: InstantMessage) -> Optional[SecureMessage]:
        packer = self.packer
        return await packer.encrypt_message(msg=msg)

    # Override
    async def sign_message(self, msg: SecureMessage) -> Optional[ReliableMessage]:
        packer = self.packer
        return await packer.sign_message(msg=msg)

    # # Override
    # async def serialize_message(self, msg: ReliableMessage) -> Optional[bytes]:
    #     packer = self.packer
    #     return await packer.serialize_message(msg=msg)
    #
    # # Override
    # async def deserialize_message(self, data: bytes) -> Optional[ReliableMessage]:
    #     packer = self.packer
    #     return await packer.deserialize_message(data=data)

    # Override
    async def verify_message(self, msg: ReliableMessage) -> Optional[SecureMessage]:
        packer = self.packer
        return await packer.verify_message(msg=msg)

    # Override
    async def decrypt_message(self, msg: SecureMessage) -> Optional[InstantMessage]:
        packer = self.packer
        return await packer.decrypt_message(msg=msg)

    #
    #   Interfaces for Processing Message
    #

    # Override
    async def process_package(self, data: bytes) -> List[bytes]:
        processor = self.processor
        return await processor.process_package(data=data)

    # Override
    async def process_reliable_message(self, msg: ReliableMessage) -> List[ReliableMessage]:
        processor = self.processor
        return await processor.process_reliable_message(msg=msg)

    # Override
    async def process_secure_message(self, msg: SecureMessage, r_msg: ReliableMessage) -> List[SecureMessage]:
        processor = self.processor
        return await processor.process_secure_message(msg=msg, r_msg=r_msg)

    # Override
    async def process_instant_message(self, msg: InstantMessage, r_msg: ReliableMessage) -> List[InstantMessage]:
        processor = self.processor
        return await processor.process_instant_message(msg=msg, r_msg=r_msg)

    # Override
    async def process_content(self, content: Content, r_msg: ReliableMessage) -> List[Content]:
        processor = self.processor
        return await processor.process_content(content=content, r_msg=r_msg)
