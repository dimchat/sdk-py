# -*- coding: utf-8 -*-
#
#   DIMP : Decentralized Instant Messaging Protocol
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

import weakref
from typing import Optional

from dimp import Base64Data
from dimp import ID
from dimp import InstantMessage, SecureMessage, ReliableMessage

from ..crypto import EncryptedBundle

from .secure_delegate import SecureMessageDelegate


class SecureMessagePacker:

    def __init__(self, messenger: SecureMessageDelegate):
        super().__init__()
        self.__transformer = weakref.ref(messenger)

    @property
    def delegate(self) -> Optional[SecureMessageDelegate]:
        return self.__transformer()

    """
        Decrypt the Secure Message to Instant Message
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            +----------+      +----------+
            | sender   |      | sender   |
            | receiver |      | receiver |
            | time     |  ->  | time     |
            |          |      |          |  1. PW      = decrypt(key, receiver.SK)
            | data     |      | content  |  2. content = decrypt(data, PW)
            | key/keys |      +----------+
            +----------+
    """

    async def _decode_key(self, msg: SecureMessage, receiver: ID) -> Optional[EncryptedBundle]:
        """ Decodes the encrypted key map from a SecureMessage """
        msg_keys = msg.encrypted_keys
        if msg_keys is None:
            # get from 'key'
            base64 = msg.get('key')
            if base64 is None:
                # broadcast message?
                # reuse key?
                return None
            msg_keys = {
                str(receiver): base64
            }
        transformer = self.delegate
        assert transformer is not None, 'secure message delegate not found'
        return await transformer.decode_key(keys=msg_keys, receiver=receiver, msg=msg)

    async def decrypt_message(self, msg: SecureMessage, receiver: ID) -> Optional[InstantMessage]:
        """
        Decrypt message, replace encrypted 'data' with 'content' field

        :param msg:      encrypted message
        :param receiver: actual receiver (local user)
        :return: InstantMessage object
        """
        assert receiver.is_user, 'receiver error: %s' % receiver
        transformer = self.delegate
        assert transformer is not None, 'secure message delegate not found'

        #
        #   1. Decode 'message.key' to encrypted symmetric key data
        #
        bundle = await self._decode_key(msg=msg, receiver=receiver)
        if bundle is None or bundle.empty:
            # broadcast message?
            # reuse key?
            key_data = None
        else:
            #
            #   2. Decrypt 'message.key' with receiver's private key
            #
            key_data = await transformer.decrypt_key(bundle=bundle, receiver=receiver, msg=msg)
            if key_data is None or len(key_data) == 0:
                # A: my visa updated but the sender doesn't got the new one;
                # B: key data error.
                raise ValueError('failed to decrypt message key: %s %s => %s, %s'
                                 % (bundle, msg.sender, receiver, msg.group))
                # TODO: check whether my visa key is changed, push new visa to this contact

        #
        #   3. Deserialize message key from data (JsON / ProtoBuf / ...)
        #      (if key is empty, means it should be reused, get it from key cache)
        #
        password = await transformer.deserialize_key(data=key_data, msg=msg)
        if password is None:
            # A: key data is empty, and cipher key not found from local storage;
            # B: key data error.
            raise ValueError('failed to get message key: %d byte(s) %s => %s, %s'
                             % (0 if key_data is None else len(key_data), msg.sender, receiver, msg.group))
            # TODO: ask the sender to send again (with new message key)

        #
        #   4. Decode 'message.data' to encrypted content data
        #
        msg_data = msg.data
        ciphertext = None if msg_data is None else msg_data.binary
        if ciphertext is None:
            return None
        assert len(ciphertext) > 0, 'failed to decode message data: %s => %s, %s' % (msg.sender, receiver, msg.group)

        #
        #   5. Decrypt 'message.data' with symmetric key
        #
        body = await transformer.decrypt_content(data=ciphertext, key=password, msg=msg)
        if body is None or len(body) == 0:
            # A: password is a reused key loaded from local storage, but it's expired;
            # B: key error.
            raise ValueError('failed to decrypt message data with key: %s, data length: %d bytes %s => %s, %s'
                             % (password, len(ciphertext), msg.sender, receiver, msg.group))
            # TODO: ask the sender to send again
        assert len(body) > 0, 'message data should not be empty: %s => %s, %s' % (msg.sender, receiver, msg.group)

        #
        #   6. Deserialize message content from data (JsON / ProtoBuf / ...)
        #
        content = await transformer.deserialize_content(data=body, key=password, msg=msg)
        if content is None:
            # assert False, 'failed to deserialize content: %d byte(s) %s => %s, %s'\
            #               % (len(body), msg.sender, receiver, msg.group)
            return None

        # TODO: check attachment for File/Image/Audio/Video message content
        #      if URL exists, means file data was uploaded to a CDN,
        #          1. save password as 'content.key';
        #          2. try to download file data from CDN;
        #          3. decrypt downloaded data with 'content.key'.
        #      (do it by application)
        #

        # OK, pack message
        info = msg.copy_dictionary()
        info.pop('key', None)
        info.pop('keys', None)
        info.pop('data', None)
        info['content'] = content.dictionary
        return InstantMessage.parse(msg=info)

    """
        Sign the Secure Message to Reliable Message
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            +----------+      +----------+
            | sender   |      | sender   |
            | receiver |      | receiver |
            | time     |  ->  | time     |
            |          |      |          |
            | data     |      | data     |
            | key/keys |      | key/keys |
            +----------+      | signature|  1. signature = sign(data, sender.SK)
                              +----------+
    """

    async def sign_message(self, msg: SecureMessage) -> Optional[ReliableMessage]:
        """
        Sign message.data, add 'signature' field

        :param msg: encrypted message
        :return: ReliableMessage object
        """
        transformer = self.delegate
        assert transformer is not None, 'secure message delegate not found'

        #
        #   0. decode message data
        #
        msg_data = msg.data
        ciphertext = None if msg_data is None else msg_data.binary
        if ciphertext is None:
            return None
        assert len(ciphertext) > 0, 'failed to decode message data: %s => %s, %s'\
                                    % (msg.sender, msg.receiver, msg.group)

        #
        #   1. Sign 'message.data' with sender's private key
        #
        signature = await transformer.sign_data(data=ciphertext, msg=msg)
        if signature is None:
            return None
        assert len(signature) > 0, 'failed to sign message: %d byte(s) %s => %s, %s'\
                                   % (len(ciphertext), msg.sender, msg.receiver, msg.group)

        #
        #   2. Encode 'message.signature' to String (Base64)
        #
        base64 = Base64Data.create(binary=signature)
        assert not base64.empty, 'failed to encode signature: %d byte(s) %s => %s, %s'\
                                 % (len(signature), msg.sender, msg.receiver, msg.group)

        # OK, pack message
        info = msg.copy_dictionary()
        info['signature'] = base64.serialize()
        return ReliableMessage.parse(msg=info)
