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

from typing import Optional

from mkm.format import utf8_encode, utf8_decode, json_encode, json_decode
from dimp import InstantMessage, SecureMessage, ReliableMessage
from dimp import Packer

from .core import TwinsHelper
from .msg import InstantMessagePacker, SecureMessagePacker, ReliableMessagePacker

from .facebook import Facebook
from .messenger import Messenger


class MessagePacker(TwinsHelper, Packer):

    def __init__(self, facebook: Facebook, messenger: Messenger):
        super().__init__(facebook=facebook, messenger=messenger)
        self.__instant_packer = InstantMessagePacker(messenger=messenger)
        self.__secure_packer = SecureMessagePacker(messenger=messenger)
        self.__reliablePacker = ReliableMessagePacker(messenger=messenger)

    @property
    def facebook(self) -> Facebook:
        barrack = super().facebook
        assert isinstance(barrack, Facebook), 'barrack error: %s' % barrack
        return barrack

    @property
    def messenger(self) -> Messenger:
        transceiver = super().messenger
        assert isinstance(transceiver, Messenger), 'transceiver error: %s' % transceiver
        return transceiver

    @property
    def instant_packer(self) -> InstantMessagePacker:
        return self.__instant_packer

    @property
    def secure_packer(self) -> SecureMessagePacker:
        return self.__secure_packer

    @property
    def reliable_packer(self) -> ReliableMessagePacker:
        return self.__reliablePacker

    #
    #   InstantMessage -> SecureMessage -> ReliableMessage -> Data
    #

    # Override
    def encrypt_message(self, msg: InstantMessage) -> Optional[SecureMessage]:
        # TODO: check receiver before calling this, make sure the visa.key exists;
        #       otherwise, suspend this message for waiting receiver's visa/meta;
        #       if receiver is a group, query all members' visa too!

        # NOTICE: before sending group message, you can decide whether expose the group ID
        #       (A) if you don't want to expose the group ID,
        #           you can split it to multi-messages before encrypting,
        #           replace the 'receiver' to each member and keep the group hidden in the content;
        #           in this situation, the packer will use the personal message key (user to user);
        #       (B) if the group ID is overt, no need to worry about the exposing,
        #           you can keep the 'receiver' being the group ID, or set the group ID as 'group'
        #           when splitting to multi-messages to let the remote packer knows it;
        #           in these situations, the local packer will use the group msg key (user to group)
        #           to encrypt the message, and the remote packer can get the overt group ID before
        #           decrypting to take the right message key.
        receiver = msg.receiver

        #
        #   1. get message key with direction (sender -> receiver) or (sender -> group)
        #
        password = self.messenger.get_encrypt_key(msg=msg)
        assert password is not None, 'failed to get msg key: %s => %s, %s' % (msg.sender, receiver, msg.get('group'))

        #
        #   2. encrypt 'content' to 'data' for receiver/group members
        #
        if receiver.is_group:
            # group message
            members = self.facebook.members(identifier=receiver)
            assert len(members) > 0, 'group not ready: %s' % receiver
            # a station will never send group message, so here must be a client;
            # the client messenger should check the group's meta & members before encrypting,
            # so we can trust that the group members MUST exist here.
            s_msg = self.instant_packer.encrypt_message(msg=msg, password=password, members=members)
        else:
            # personal message (or split group message)
            s_msg = self.instant_packer.encrypt_message(msg=msg, password=password)
        if s_msg is None:
            # public key for encryption not found
            # TODO: suspend this message for waiting receiver's meta
            # assert False, 'failed to encrypt message: %s' % msg
            return None

        # NOTICE: copy content type to envelope
        #         this help the intermediate nodes to recognize message type
        s_msg.envelope.type = msg.content.type

        # OK
        return s_msg

    # Override
    def sign_message(self, msg: SecureMessage) -> ReliableMessage:
        assert len(msg.data) > 0, 'message data cannot be empty: %s' % msg
        # sign 'data' by sender
        return self.secure_packer.sign_message(msg=msg)

    # Override
    def serialize_message(self, msg: ReliableMessage) -> bytes:
        js = json_encode(obj=msg.dictionary)
        return utf8_encode(string=js)

    #
    #   Data -> ReliableMessage -> SecureMessage -> InstantMessage
    #

    def deserialize_message(self, data: bytes) -> Optional[ReliableMessage]:
        js = utf8_decode(data=data)
        if js is None:
            # assert False, 'message data error: %d' % len(data)
            return None
        dictionary = json_decode(string=js)
        # TODO: translate short keys
        #       'S' -> 'sender'
        #       'R' -> 'receiver'
        #       'W' -> 'time'
        #       'T' -> 'type'
        #       'G' -> 'group'
        #       ------------------
        #       'D' -> 'data'
        #       'V' -> 'signature'
        #       'K' -> 'key'
        #       ------------------
        #       'M' -> 'meta'
        #       'P' -> 'visa'
        return ReliableMessage.parse(msg=dictionary)

    def verify_message(self, msg: ReliableMessage) -> Optional[SecureMessage]:
        # TODO: make sure sender's meta exists before verifying message
        facebook = self.facebook
        sender = msg.sender
        # [Meta Protocol]
        meta = msg.meta
        if meta is not None:
            facebook.save_meta(meta=meta, identifier=sender)
        # [Visa Protocol]
        visa = msg.visa
        if visa is not None:
            facebook.save_document(document=visa)
        #
        # NOTICE: check [Visa Protocol] before calling this
        #       make sure the sender's meta(visa) exists
        #       (do it by application)
        #
        assert len(msg.signature) > 0, 'message signature cannot be empty: %s' % msg
        # verify 'data' with 'signature'
        return self.reliable_packer.verify_message(msg=msg)

    def decrypt_message(self, msg: SecureMessage) -> Optional[InstantMessage]:
        # TODO: check receiver before calling this, make sure you are the receiver,
        #       or you are a member of the group when this is a group message,
        #       so that you will have a private key (decrypt key) to decrypt it.
        facebook = self.facebook
        receiver = msg.receiver
        user = facebook.select_user(receiver=receiver)
        if user is None:
            # not for you?
            raise LookupError('receiver error: %s, from %s, %s' % (receiver, msg.sender, msg.group))
        assert len(msg.data) > 0, 'message data empty: %s => %s, %s' % (msg.sender, msg.receiver, msg.group)
        # decrypt 'data' to 'content'
        return self.secure_packer.decrypt_message(msg=msg, receiver=user.identifier)
        # TODO: check top-secret message
        #       (do it by application)
