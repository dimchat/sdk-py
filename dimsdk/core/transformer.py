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

from abc import ABC, abstractmethod
from typing import Optional, Any, Dict

from dimp import SymmetricKey
from dimp import ID
from dimp import Content
from dimp import InstantMessage, SecureMessage, ReliableMessage
from dimp import BaseMessage

from ..crypto import EncryptedBundle
from ..mkm import EntityDelegate
from ..msg import InstantMessageDelegate, SecureMessageDelegate, ReliableMessageDelegate

from .compressor import Compressor


class Transformer(InstantMessageDelegate, SecureMessageDelegate, ReliableMessageDelegate, ABC):
    """
        Message Transformer
        ~~~~~~~~~~~~~~~~~~~
        Converting message format between PlainMessage and NetworkMessage
    """

    @property  # protected
    @abstractmethod
    def facebook(self) -> EntityDelegate:
        raise NotImplemented

    @property  # protected
    @abstractmethod
    def compressor(self) -> Compressor:
        raise NotImplemented

    async def serialize_message(self, msg: ReliableMessage) -> Optional[bytes]:
        """
        Serialize network message

        :param msg: network message
        :return: data package
        """
        msg_info = msg.dictionary
        compressor = self.compressor
        return compressor.compress_reliable_message(msg=msg_info)

    async def deserialize_message(self, data: bytes) -> Optional[ReliableMessage]:
        """
        Deserialize network message

        :param data: data package
        :return: network message
        """
        compressor = self.compressor
        info = compressor.extract_reliable_message(data=data)
        return ReliableMessage.parse(msg=info)

    #
    #   InstantMessageDelegate
    #

    # Override
    async def serialize_content(self, content: Content, key: SymmetricKey, msg: InstantMessage) -> bytes:
        # NOTICE: check attachment for File/Image/Audio/Video message content
        #         before serialize content, this job should be do in subclass
        msg_body = content.dictionary
        key_info = key.dictionary
        compressor = self.compressor
        return compressor.compress_content(content=msg_body, key=key_info)

    # Override
    async def encrypt_content(self, data: bytes, key: SymmetricKey, msg: InstantMessage) -> bytes:
        # store 'IV' in msg for AES encryption
        msg_info = msg.dictionary
        return key.encrypt(plaintext=data, extra=msg_info)

    # # Override
    # async def encode_data(self, data: bytes, msg: InstantMessage) -> Any:
    #     if BaseMessage.is_broadcast(msg=msg):
    #         # broadcast message content will not be encrypted (just encoded to JsON),
    #         # so no need to encode to Base64 here
    #         return utf8_decode(data=data)
    #     # message content had been encrypted by a symmetric key,
    #     # so the data should be encoded here (with algorithm 'base64' as default).
    #     return TransportableData.encode(data=data)

    # Override
    async def serialize_key(self, key: SymmetricKey, msg: InstantMessage) -> Optional[bytes]:
        if BaseMessage.is_broadcast(msg=msg):
            # broadcast message has no key
            return None
        key_info = key.dictionary
        compressor = self.compressor
        return compressor.compress_symmetric_key(key=key_info)

    # Override
    async def encrypt_key(self, data: bytes, receiver: ID, msg: InstantMessage) -> Optional[EncryptedBundle]:
        assert not BaseMessage.is_broadcast(msg=msg), 'broadcast message has no key: %s' % msg
        assert receiver.is_user, 'receiver error: %s' % receiver
        # TODO: make sure the receiver's public key exists
        facebook = self.facebook
        contact = await facebook.get_user(identifier=receiver)
        if contact is not None:
            # encrypt with public key of the receiver (or group member)
            return await contact.encrypt_bundle(plaintext=data)
        else:
            assert False, 'failed to encrypt message key for receiver: %s' % receiver

    # Override
    async def encode_key(self, bundle: EncryptedBundle, receiver: ID, msg: InstantMessage) -> Dict[str, Any]:
        assert not BaseMessage.is_broadcast(msg=msg), 'broadcast message has no key: %s' % msg
        # message key had been encrypted by a public key,
        # so the data should be encode here (with algorithm 'base64' as default).
        return bundle.encode(identifier=receiver)
        # TODO: check for wildcard

    #
    #   SecureMessageDelegate
    #

    # Override
    async def decode_key(self, keys: Dict, receiver: ID, msg: SecureMessage) -> Optional[EncryptedBundle]:
        assert not BaseMessage.is_broadcast(msg=msg), 'broadcast message has no key: %s' % msg
        assert receiver.is_user, 'receiver error: %s' % receiver
        facebook = self.facebook
        user = await facebook.get_user(identifier=receiver)
        if user is not None:
            # decode key bundle for all terminals
            terminals = await user.terminals
            return EncryptedBundle.decode(keys=keys, identifier=receiver, terminals=terminals)
        else:
            assert False, 'failed to decode key: %s => %s, %s' % (msg.sender, receiver, msg.group)

    # Override
    async def decrypt_key(self, bundle: EncryptedBundle, receiver: ID, msg: SecureMessage) -> Optional[bytes]:
        # NOTICE: the receiver must be a member ID
        #         if it's a group message
        assert not BaseMessage.is_broadcast(msg=msg), 'broadcast message has no key'
        assert receiver.is_user, 'receiver error: %s' % receiver
        facebook = self.facebook
        user = await facebook.get_user(identifier=receiver)
        if user is not None:
            # decrypt with private key of the receiver (or group member)
            return await user.decrypt_bundle(bundle=bundle)
        else:
            assert False, 'failed to create local user: %s' % msg.receiver

    # Override
    async def deserialize_key(self, data: Optional[bytes], msg: SecureMessage) -> Optional[SymmetricKey]:
        assert not BaseMessage.is_broadcast(msg=msg), 'broadcast message has no key: %s' % msg
        if data is None:
            # assert False, 'reused key? get it from cache: %s => %s, %s' % (msg.sender, msg.receiver, msg.group)
            return None
        compressor = self.compressor
        info = compressor.extract_symmetric_key(data=data)
        return SymmetricKey.parse(key=info)

    # # Override
    # async def decode_data(self, data: Any, msg: SecureMessage) -> Optional[bytes]:
    #     if BaseMessage.is_broadcast(msg=msg):
    #         # broadcast message content will not be encrypted (just encoded to JsON),
    #         # so return the string data directly
    #         if isinstance(data, str):
    #             return utf8_encode(string=data)
    #         else:
    #             # assert False, 'content data error: %s' % data
    #             return None
    #     else:
    #         # message content had been encrypted by a symmetric key,
    #         # so the data should be encoded here (with algorithm 'base64' as default).
    #         return TransportableData.decode(data)

    # Override
    async def decrypt_content(self, data: bytes, key: SymmetricKey, msg: SecureMessage) -> Optional[bytes]:
        # check 'IV' in msg for AES decryption
        msg_info = msg.dictionary
        return key.decrypt(ciphertext=data, params=msg_info)

    # Override
    async def deserialize_content(self, data: bytes, key: SymmetricKey, msg: SecureMessage) -> Optional[Content]:
        # assert len(msg.data) > 0, 'message data empty: %s' % msg.dictionary
        key_info = key.dictionary
        compressor = self.compressor
        info = compressor.extract_content(data=data, key=key_info)
        return Content.parse(content=info)
        # NOTICE: check attachment for File/Image/Audio/Video message content
        #         after deserialize content, this job should be do in subclass

    # Override
    # noinspection PyUnusedLocal
    async def sign_data(self, data: bytes, msg: SecureMessage) -> bytes:
        sender = msg.sender
        facebook = self.facebook
        user = await facebook.get_user(identifier=sender)
        if user is not None:
            return await user.sign(data=data)
        else:
            assert False, 'failed to sign message data for sender: %s' % sender

    # # Override
    # async def encode_signature(self, signature: bytes, msg: SecureMessage) -> str:
    #     return TransportableData.encode(data=signature)

    #
    #   ReliableMessageDelegate
    #

    # # Override
    # async def decode_signature(self, signature: Any, msg: ReliableMessage) -> Optional[bytes]:
    #     return TransportableData.decode(signature)

    # Override
    async def verify_data_signature(self, data: bytes, signature: bytes, msg: ReliableMessage) -> bool:
        sender = msg.sender
        facebook = self.facebook
        contact = await facebook.get_user(identifier=sender)
        if contact is not None:
            return await contact.verify(data=data, signature=signature)
        else:
            assert False, 'failed to verify signature for sender: %s' % sender
