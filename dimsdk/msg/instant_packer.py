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
from typing import Optional, List

from dimp import SymmetricKey
from dimp import ID
from dimp import InstantMessage, SecureMessage

from ..crypto import EncryptedBundle

from .instant_delegate import InstantMessageDelegate


"""
    Generic for Encrypted Bundle
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
try:
    import collections.abc as abc
    BundleMap = abc.MutableMapping[ID, EncryptedBundle]
except TypeError:
    import typing
    BundleMap = typing.MutableMapping[ID, EncryptedBundle]


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
            +----------+      | keys     |  2. key  = encrypt(PW, receiver.PK)
                              +----------+
    """

    async def encrypt_message(self, msg: InstantMessage, password: SymmetricKey,
                              members: List[ID] = None) -> Optional[SecureMessage]:
        """
        Encrypt message, replace 'content' field with encrypted 'data'

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
        body = await transformer.serialize_content(content=msg.content, password=password, msg=msg)
        if body is None:
            # assert False, f'failed to serialize content: {msg.content}'
            return None
        assert len(body) > 0, f'failed to serialize content: {msg.content}'

        #
        #   2. Encrypt content data to 'message.data' with symmetric key
        #
        ciphertext = await transformer.encrypt_content(data=body, password=password, msg=msg)
        if ciphertext is None:
            # assert False, f'failed to encrypt content with key: {password}'
            return None
        assert len(ciphertext) > 0, f'failed to encrypt content with key: {password}'

        #
        #   3. Encode 'message.data' to String (Base64)
        #
        # ... do it in SecureMessage.from_instant_message()

        #
        #   4. Serialize message key to data (JsON / ProtoBuf / ...)
        #
        pwd = await transformer.serialize_key(password=password, msg=msg)
        # NOTICE:
        #    if the key is reused, the msg must be updated with key digest.

        # check serialized key data,
        # if key data is null here, build the secure message directly.
        if pwd is None:
            # A) broadcast message has no key
            # B) reused key
            return SecureMessage.from_instant_message(i_msg=msg, data=ciphertext, bundles=None)
        # encrypt + encode key

        if members is None:
            # personal message
            receiver = msg.receiver
            assert receiver.is_user, f'message.receiver error: {receiver}'
            members = [receiver]
        # else:
        #     # group message
        #     receiver = msg.receiver
        #     assert receiver.is_group, f'message.receiver error: {receiver}'
        #     assert len(members) > 0, f'group members empty: {receiver}'

        bundle_map: BundleMap = {}
        for receiver in members:
            #
            #   5. Encrypt key data to 'message.keys' with member's public key
            #
            bundle = await transformer.encrypt_key(data=pwd, receiver=receiver, msg=msg)
            if bundle is None or bundle.is_empty:
                # public key for member not found
                # TODO: suspend this message for waiting member's visa
                continue
            bundle_map[receiver] = bundle

        #
        #   6. Encode message key to String (Base64)
        #
        # ... do it in SecureMessage.from_instant_message()

        # OK, pack message
        return SecureMessage.from_instant_message(i_msg=msg, data=ciphertext, bundles=bundle_map)
        # TODO: put key digest
