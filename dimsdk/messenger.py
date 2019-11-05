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

import json
from abc import abstractmethod
from typing import Optional

from dimp import SymmetricKey, ID, Meta
from dimp import InstantMessage, SecureMessage, ReliableMessage
from dimp import ContentType, Content, ForwardContent, FileContent
from dimp import Transceiver

from .cpu import ContentProcessor

from .delegate import Callback, CompletionHandler
from .delegate import MessengerDelegate, ConnectionDelegate
from .facebook import Facebook


class Messenger(Transceiver, ConnectionDelegate):

    def __init__(self):
        super().__init__()
        self.delegate: MessengerDelegate = None
        self.__processor = ContentProcessor(messenger=self)

    #
    #  Transform
    #
    def verify_message(self, msg: ReliableMessage) -> Optional[SecureMessage]:
        facebook: Facebook = self.barrack
        sender = facebook.identifier(msg.envelope.sender)
        meta = Meta(msg.meta)
        if meta is None:
            meta = facebook.meta(identifier=sender)
            if meta is None:
                # TODO: query meta for sender from DIM network
                #       (do it by application)
                raise LookupError('failed to get meta for sender: %s' % sender)
        else:
            # [Meta Protocol]
            # save meta for sender
            if not facebook.save_meta(meta=meta, identifier=sender):
                raise ValueError('save meta error: %s, %s' % (sender, meta))
        return super().verify_message(msg=msg)

    def decrypt_message(self, msg: SecureMessage) -> Optional[InstantMessage]:
        i_msg = super().decrypt_message(msg=msg)
        # check: top-secret message
        if i_msg.content.type == ContentType.Forward:
            # [Forward Protocol]
            # do it again to drop the wrapper,
            # the secret inside the content is the real message
            content: ForwardContent = i_msg.content
            r_msg = content.forward
            secret = self.verify_decrypt(msg=r_msg)
            if secret is not None:
                return secret
            # FIXME: not for you?
        return i_msg

    def encrypt_content(self, content: Content, key: dict, msg: InstantMessage) -> bytes:
        password = SymmetricKey(key=key)
        assert password == key, 'irregular symmetric key: %s' % key
        # check attachment for File/Image/Audio/Video message content before
        if isinstance(content, FileContent):
            data = password.encrypt(data=content.data)
            # upload (encrypted) file data onto CDN and save the URL in message content
            url = self.delegate.upload_data(data=data, msg=msg)
            if url is not None:
                content.url = url
                content.data = None
        return super().encrypt_content(content=content, key=password, msg=msg)

    def decrypt_content(self, data: bytes, key: dict, msg: SecureMessage) -> Optional[Content]:
        password = SymmetricKey(key=key)
        content = super().decrypt_content(data=data, key=password, msg=msg)
        if content is None:
            return None
        # check attachment for File/Image/Audio/Video message content after
        if isinstance(content, FileContent):
            i_msg = InstantMessage.new(content=content, envelope=msg.envelope)
            # download from CDN
            file_data = self.delegate.download_data(content.url, i_msg)
            if file_data is None:
                # save symmetric key for decrypted file data after download from CDN
                content.password = password
            else:
                # decrypt file data
                content.data = password.decrypt(data=file_data)
                assert content.data is not None, 'failed to decrypt file data with key: %s' % key
                content.url = None
        return content

    #
    #  Conveniences
    #
    def encrypt_sign(self, msg: InstantMessage) -> ReliableMessage:
        # 1. encrypt 'content' to 'data' for receiver
        s_msg = self.encrypt_message(msg=msg)
        # 1.1. check group
        group = msg.content.group
        if group is not None:
            # NOTICE: this help the receiver knows the group ID
            #         when the group message separated to multi-messages,
            #         if don't want the others know you are the group members,
            #         remove it.
            s_msg.envelope.group = group
        # 1.2. copy content type to envelope
        #      NOTICE: this help the intermediate nodes to recognize message type
        s_msg.envelope.type = msg.content.type
        # 2. sign 'data' by sender
        r_msg = self.sign_message(msg=s_msg)
        # OK
        return r_msg

    def verify_decrypt(self, msg: ReliableMessage) -> Optional[InstantMessage]:
        # 1. verify 'data' with 'signature'
        s_msg = self.verify_message(msg=msg)
        if s_msg is None:
            raise ValueError('failed to verify message: %s' % msg)
        # 2. check group message
        receiver = self.barrack.identifier(msg.envelope.receiver)
        if receiver.type.is_group():
            # TODO: split it
            pass
        # 3. decrypt 'data' to 'content'
        i_msg = self.decrypt_message(msg=s_msg)
        # OK
        return i_msg

    #
    #   Send message
    #
    def send_message(self, msg: InstantMessage, callback: Callback=None, split: bool=True) -> bool:
        """
        Send message (secured + certified) to target station

        :param msg:      instant message
        :param callback: callback function
        :param split:    if it's a group message, split it before sending out
        :return:         False on data/delegate error
        """
        # transforming
        r_msg = self.encrypt_sign(msg=msg)
        if r_msg is None:
            raise AssertionError('failed to encrypt and sign message: %s' % msg)
        # trying to send out
        ok = True
        receiver = self.barrack.identifier(msg.envelope.receiver)
        if split and receiver.type.is_group():
            group = self.barrack.group(identifier=receiver)
            if group is None:
                raise LookupError('failed to create group: %s' % receiver)
            members = group.members
            if members is None or len(members) == 0:
                # FIXME: query group members from sender
                messages = None
            else:
                messages = r_msg.split(members=members)
            if messages is None:
                # failed to split msg, send it to group
                ok = self.__send_message(msg=r_msg, callback=callback)
            else:
                # sending group message one by one
                for r_msg in messages:
                    if not self.__send_message(msg=r_msg, callback=callback):
                        ok = False
        else:
            ok = self.__send_message(msg=r_msg, callback=callback)
        # TODO: if OK, set iMsg.state = sending; else set iMsg.state = waiting
        return ok

    def __send_message(self, msg: ReliableMessage, callback: Callback) -> bool:
        data = json.dumps(msg).encode('utf-8')
        handler = MessageCallback(msg=msg, cb=callback)
        delegate: MessengerDelegate = self.delegate
        return delegate.send_package(data=data, handler=handler)

    @abstractmethod
    def send_content(self, content: Content, receiver: ID) -> bool:
        """
        Send content to receiver

        :param content: message content
        :param receiver: receiver ID
        :return: True on success
        """
        pass

    #
    #   Received message
    #
    def received_package(self, data: bytes) -> bool:
        """
        Processing received message package

        :param data: message data
        :return: True on success
        """
        try:
            # deserialize message
            r_msg = self.deserialize_message(data=data)
            # process message
            return self.process_message(msg=r_msg)
        except ValueError:
            return False

    def process_message(self, msg: ReliableMessage) -> bool:
        # verify
        s_msg = self.verify_message(msg=msg)
        if s_msg is None:
            raise ValueError('failed to verify message: %s' % msg)
        # decrypt
        i_msg = self.decrypt_message(msg=s_msg)
        if i_msg is None:
            # cannot decrypt this message, not for you?
            return self.deliver_message(msg=msg)
        content = i_msg.content
        if isinstance(content, ForwardContent):
            # this top-secret message was delegated to you to forward it
            return self.forward_message(msg=content.forward)
        return self.__processor.process(content=content, envelope=i_msg.envelope)

    @abstractmethod
    def deliver_message(self, msg: ReliableMessage) -> bool:
        """
        Deliver message to the receiver, or broadcast to neighbours

        :param msg: reliable message
        :return: True on success
        """
        pass

    @abstractmethod
    def forward_message(self, msg: ReliableMessage) -> bool:
        """
        Re-pack and deliver (Top-Secret) message to the real receiver

        :param msg: top-secret message
        :return: True on success
        """
        pass


class MessageCallback(CompletionHandler):

    def __init__(self, msg: ReliableMessage, cb: Callback):
        super().__init__()
        self.msg = msg
        self.callback = cb

    def success(self):
        if self.callback is not None:
            self.callback.finished(result=self.msg, error=None)

    def failed(self, error):
        if self.callback is not None:
            self.callback.finished(result=self.msg, error=error)
