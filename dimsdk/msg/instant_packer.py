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
from typing import Optional, Any, List, Dict

from dimp import SymmetricKey
from dimp import ID
from dimp import InstantMessage, SecureMessage
from dimp import BaseMessage
from dimp import PlainData, Base64Data

from ..crypto import EncryptedBundle

from .instant_delegate import InstantMessageDelegate


class InstantMessagePacker:

    def __init__(self, messenger: InstantMessageDelegate):
        super().__init__()
        self.__transformer = weakref.ref(messenger)

    @property
    def delegate(self) -> Optional[InstantMessageDelegate]:
        return self.__transformer()

    """
        Encrypt the Instant Message to Secure Message
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            +----------+      +----------+
            | sender   |      | sender   |
            | receiver |      | receiver |
            | time     |  ->  | time     |
            |          |      |          |
            | content  |      | data     |  1. data = encrypt(content, PW)
            +----------+      | key/keys |  2. key  = encrypt(PW, receiver.PK)
                              +----------+
    """

    async def encrypt_message(self, msg: InstantMessage, password: SymmetricKey,
                              members: List[ID] = None) -> Optional[SecureMessage]:
        """
        1. Encrypt message, replace 'content' field with encrypted 'data'
        2. Encrypt group message, replace 'content' field with encrypted 'data'

        :param msg:      plain message
        :param password: symmetric key
        :param members:  group members for group message
        :return: SecureMessage object, None on visa not found
        """
        # TODO: check attachment for File/Image/Audio/Video message content
        #       (do it by application)
        transformer = self.delegate
        assert transformer is not None, 'instant message delegate not found'

        #
        #   1. Serialize 'message.content' to data (JsON / ProtoBuf / ...)
        #
        body = await transformer.serialize_content(content=msg.content, key=password, msg=msg)
        if body is None:
            return None
        assert len(body) > 0, 'failed to serialize content: %s' % msg.content

        #
        #   2. Encrypt content data to 'message.data' with symmetric key
        #
        ciphertext = await transformer.encrypt_content(data=body, key=password, msg=msg)
        if ciphertext is None:
            return None
        assert len(ciphertext) > 0, 'failed to encrypt content with key: %s' % password

        #
        #   3. Encode 'message.data' to String (Base64)
        #
        if BaseMessage.is_broadcast(msg=msg):
            # broadcast message content will not be encrypted (just encoded to JsON),
            # so no need to encode to Base64 here
            encoded_data = PlainData.create(binary=ciphertext)
        else:
            # message content had been encrypted by a symmetric key,
            # so the data should be encoded here (with algorithm 'base64' as default).
            encoded_data = Base64Data.create(binary=ciphertext)
        assert not encoded_data.empty, 'failed to encode content data: %s' % ciphertext

        #
        #   4. Serialize message key to data (JsON / ProtoBuf / ...)
        #
        pwd = await transformer.serialize_key(key=password, msg=msg)
        # NOTICE:
        #    if the key is reused, the msg must be updated with key digest.
        info = msg.copy_dictionary()

        # replace 'content' with encrypted 'data
        info.pop('content', None)
        info['data'] = encoded_data.serialize()

        # check serialized key data,
        # if key data is null here, build the secure message directly.
        if pwd is None:
            # A) broadcast message has no key
            # B) reused key
            return SecureMessage.parse(msg=info)
        # encrypt + encode key

        if members is None:
            # personal message
            receiver = msg.receiver
            assert receiver.is_user, 'message.receiver error: %s' % receiver
            members = [receiver]
        else:
            # group message
            receiver = msg.receiver
            assert receiver.is_group, 'message.receiver error: %s' % receiver
            assert len(members) > 0, 'group members empty: %s' % receiver

        bundle_map: Dict[ID, EncryptedBundle] = {}
        for receiver in members:
            #
            #   5. Encrypt key data to 'message.key/keys' with receiver's public key
            #
            bundle = await transformer.encrypt_key(pwd, receiver=receiver, msg=msg)
            if bundle is None or bundle.empty:
                # public key for encryption not found
                # TODO: suspend this message for waiting receiver's visa
                continue
            bundle_map[receiver] = bundle

        #
        #   6. Encode message key to String (Base64)
        #
        msg_keys = await self._encode_keys(bundle_map=bundle_map, msg=msg)
        # if msg_keys is None or len(msg_keys) == 0:
        #     # public key for member(s) not found
        #     # TODO: suspend this message for waiting member's visa
        #     return None

        # insert as 'keys'
        info['keys'] = msg_keys

        # OK, pack message
        return SecureMessage.parse(msg=info)

    async def _encode_keys(self, bundle_map: Dict[ID, EncryptedBundle], msg: InstantMessage) -> Dict[str, Any]:
        """ Encodes encrypted key bundles to a message-compatible map """
        transformer = self.delegate
        assert transformer is not None, 'instant message delegate not found'
        msg_keys: Dict[str, Any] = {}
        for receiver in bundle_map:
            bundle = bundle_map.get(receiver)
            encoded_keys = await transformer.encode_key(bundle=bundle, receiver=receiver, msg=msg)
            if encoded_keys is None or len(encoded_keys) == 0:
                # assert False, 'failed to encode key data: %s' % receiver
                continue
            # insert to 'message.keys' with ID + terminal
            msg_keys.update(encoded_keys)
        # TODO: put key digest
        return msg_keys
