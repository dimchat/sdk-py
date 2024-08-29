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
from dimp import Transceiver, Packer, Processor

from .delegate import CipherKeyDelegate


class Messenger(Transceiver, Packer, Processor, ABC):

    @property
    @abstractmethod
    def key_cache(self) -> CipherKeyDelegate:
        """ Delegate for Cipher Key """
        raise NotImplemented

    @property
    @abstractmethod
    def packer(self) -> Packer:
        """ Delegate for Packing Message """
        raise NotImplemented

    @property
    @abstractmethod
    def processor(self) -> Processor:
        """ Delegate for Processing Message """
        raise NotImplemented

    #
    #   Interfaces for Cipher Key
    #

    async def get_encrypt_key(self, msg: InstantMessage) -> Optional[SymmetricKey]:
        sender = msg.sender
        target = CipherKeyDelegate.destination_for_message(msg=msg)
        delegate = self.key_cache
        return await delegate.get_cipher_key(sender=sender, receiver=target, generate=True)

    async def get_decrypt_key(self, msg: SecureMessage) -> Optional[SymmetricKey]:
        sender = msg.sender
        target = CipherKeyDelegate.destination_for_message(msg=msg)
        delegate = self.key_cache
        return await delegate.get_cipher_key(sender=sender, receiver=target, generate=False)

    async def cache_decrypt_key(self, key: SymmetricKey, msg: SecureMessage):
        sender = msg.sender
        target = CipherKeyDelegate.destination_for_message(msg=msg)
        delegate = self.key_cache
        return await delegate.cache_cipher_key(key=key, sender=sender, receiver=target)

    #
    #   Interfaces for Packing Message
    #

    # Override
    async def encrypt_message(self, msg: InstantMessage) -> Optional[SecureMessage]:
        delegate = self.packer
        return await delegate.encrypt_message(msg=msg)

    # Override
    async def sign_message(self, msg: SecureMessage) -> Optional[ReliableMessage]:
        delegate = self.packer
        return await delegate.sign_message(msg=msg)

    # Override
    async def serialize_message(self, msg: ReliableMessage) -> Optional[bytes]:
        delegate = self.packer
        return await delegate.serialize_message(msg=msg)

    # Override
    async def deserialize_message(self, data: bytes) -> Optional[ReliableMessage]:
        delegate = self.packer
        return await delegate.deserialize_message(data=data)

    # Override
    async def verify_message(self, msg: ReliableMessage) -> Optional[SecureMessage]:
        delegate = self.packer
        return await delegate.verify_message(msg=msg)

    # Override
    async def decrypt_message(self, msg: SecureMessage) -> Optional[InstantMessage]:
        delegate = self.packer
        return await delegate.decrypt_message(msg=msg)

    #
    #   Interfaces for Processing Message
    #

    # Override
    async def process_package(self, data: bytes) -> List[bytes]:
        delegate = self.processor
        return await delegate.process_package(data=data)

    # Override
    async def process_reliable_message(self, msg: ReliableMessage) -> List[ReliableMessage]:
        delegate = self.processor
        return await delegate.process_reliable_message(msg=msg)

    # Override
    async def process_secure_message(self, msg: SecureMessage, r_msg: ReliableMessage) -> List[SecureMessage]:
        delegate = self.processor
        return await delegate.process_secure_message(msg=msg, r_msg=r_msg)

    # Override
    async def process_instant_message(self, msg: InstantMessage, r_msg: ReliableMessage) -> List[InstantMessage]:
        delegate = self.processor
        return await delegate.process_instant_message(msg=msg, r_msg=r_msg)

    # Override
    async def process_content(self, content: Content, r_msg: ReliableMessage) -> List[Content]:
        delegate = self.processor
        return await delegate.process_content(content=content, r_msg=r_msg)

    #
    #   SecureMessageDelegate
    #

    # Override
    async def deserialize_key(self, data: Optional[bytes], msg: SecureMessage) -> Optional[SymmetricKey]:
        if data is None:
            # get key from cache with direction: sender -> receiver(group)
            return await self.get_decrypt_key(msg=msg)
        else:
            return await super().deserialize_key(data=data, msg=msg)

    # Override
    async def deserialize_content(self, data: bytes, key: SymmetricKey, msg: SecureMessage) -> Optional[Content]:
        content = await super().deserialize_content(data=data, key=key, msg=msg)
        # cache decrypt key when success
        if content is None:
            assert False, 'content error: %d' % len(data)
        else:
            # cache the key with direction: sender -> receiver(group)
            await self.cache_decrypt_key(key=key, msg=msg)
        # NOTICE: check attachment for File/Image/Audio/Video message content
        #         after deserialize content, this job should be do in subclass
        return content
