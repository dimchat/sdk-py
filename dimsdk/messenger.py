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

import weakref
from abc import abstractmethod
from typing import Optional

from dimp import SymmetricKey, ID, Meta, User
from dimp import Message, InstantMessage, SecureMessage, ReliableMessage
from dimp import Content, ForwardContent, FileContent, TextContent
from dimp import Transceiver

from .protocol import ReceiptCommand
from .delegate import Callback, CompletionHandler
from .delegate import MessengerDelegate, ConnectionDelegate
from .facebook import Facebook
from .processor import MessageProcessor


class Messenger(Transceiver, ConnectionDelegate):

    def __init__(self):
        super().__init__()
        self.__context: dict = {}
        self.__processor: MessageProcessor = None
        self.__delegate: weakref.ReferenceType = None

    #
    #   Delegate for sending data
    #
    @property
    def delegate(self) -> Optional[MessengerDelegate]:
        if self.__delegate is not None:
            return self.__delegate()

    @delegate.setter
    def delegate(self, value: Optional[MessengerDelegate]):
        assert value is not None, 'message delegate should not be empty'
        self.__delegate = weakref.ref(value)

    #
    #   Environment variables as context
    #
    @property
    def context(self) -> dict:
        return self.__context

    def get_context(self, key: str):
        return self.__context.get(key)

    def set_context(self, key: str, value):
        if value is None:
            self.__context.pop(key, None)
        else:
            self.__context[key] = value

    #
    #   Data source for getting entity info
    #
    @property
    def facebook(self) -> Facebook:
        barrack = self.__context.get('facebook')
        if barrack is None:
            barrack = self.barrack
            assert isinstance(barrack, Facebook), 'messenger delegate error: %s' % barrack
        return barrack

    def __select(self, receiver: ID) -> Optional[User]:
        facebook = self.facebook
        users = facebook.local_users
        if users is None or len(users) == 0:
            raise LookupError('local users should not be empty')
        elif receiver.is_broadcast:
            # broadcast message can decrypt by anyone, so just return current user
            return users[0]
        if receiver.type.is_group():
            # group message (recipient not designated)
            members = facebook.members(identifier=receiver)
            if members is None or len(members) == 0:
                # TODO: query group members
                #       (do it by application)
                return None
            for item in users:
                if item.identifier in members:
                    # set this item to be current user?
                    return item
        else:
            # 1. personal message
            # 2. split group message
            assert receiver.type.is_user(), 'receiver ID error: %s' % receiver
            for item in users:
                if item.identifier == receiver:
                    # set this item to be current user?
                    return item

    def __trim(self, msg: SecureMessage) -> Optional[SecureMessage]:
        receiver = self.facebook.identifier(msg.envelope.receiver)
        user = self.__select(receiver=receiver)
        if user is None:
            # current users not match
            msg = None
        elif receiver.type.is_group():
            # trim group message
            msg = msg.trim(member=user.identifier)
        return msg

    #
    #  Transform
    #
    def verify_message(self, msg: ReliableMessage) -> Optional[SecureMessage]:
        facebook = self.facebook
        # NOTICE: check meta before calling me
        sender = facebook.identifier(msg.envelope.sender)
        meta = msg.meta
        if meta is None:
            meta = facebook.meta(identifier=sender)
            if meta is None:
                # NOTICE: the application will query meta automatically
                # save this message in a queue waiting sender's meta response
                self.suspend_message(msg=msg)
                # raise LookupError('failed to get meta for sender: %s' % sender)
                return None
        else:
            # [Meta Protocol]
            # save meta for sender
            meta = Meta(meta)
            if not facebook.save_meta(meta=meta, identifier=sender):
                raise ValueError('save meta error: %s, %s' % (sender, meta))
        return super().verify_message(msg=msg)

    def encrypt_message(self, msg: InstantMessage) -> SecureMessage:
        s_msg = super().encrypt_message(msg=msg)
        group = msg.content.group
        if group is not None:
            # NOTICE: this help the receiver knows the group ID
            #         when the group message separated to multi-messages,
            #         if don't want the others know you are the group members,
            #         remove it.
            s_msg.envelope.group = group
        # NOTICE: copy content type to envelope
        #         this help the intermediate nodes to recognize message type
        s_msg.envelope.type = msg.content.type
        return s_msg

    def decrypt_message(self, msg: SecureMessage) -> Optional[InstantMessage]:
        # 0. trim message
        msg = self.__trim(msg=msg)
        if msg is None:
            # not for you?
            return None
        # 1. decrypt message
        i_msg = super().decrypt_message(msg=msg)
        # 2. check: top-secret message
        content = i_msg.content
        if isinstance(content, ForwardContent):
            # [Forward Protocol]
            # do it again to drop the wrapper,
            # the secret inside the content is the real message
            r_msg = content.forward
            s_msg = self.verify_message(msg=r_msg)
            if s_msg is not None:
                # verify OK, try to decrypt
                secret = self.decrypt_message(msg=s_msg)
                if secret is not None:
                    # decrypt success
                    return secret
                # NOTICE: decrypt failed, not for you?
                #         check content type in subclass, if it's a 'forward' message,
                #         it means you are asked to re-pack and forward this message
        return i_msg

    #
    #   InstantMessageDelegate
    #
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

    def encrypt_key(self, key: dict, receiver: str, msg: InstantMessage) -> Optional[bytes]:
        facebook = self.facebook
        to = facebook.identifier(receiver)
        pk = facebook.public_key_for_encryption(identifier=to)
        if pk is None:
            meta = facebook.meta(identifier=to)
            if meta is None:
                # save this message in a queue waiting receiver's meta response
                self.suspend_message(msg=msg)
                # raise LookupError('failed to get encrypt key for receiver: %s' % receiver)
                return None
        return super().encrypt_key(key=key, receiver=receiver, msg=msg)

    #
    #   SecureMessageDelegate
    #
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
    #   Send message
    #
    def send_content(self, content: Content, receiver: ID, callback: Callback=None, split: bool=True) -> bool:
        """
        Send content to receiver

        :param content: message content
        :param receiver: receiver ID
        :param callback: callback function
        :param split:    if it's a group message, split it before sending out
        :return: True on success
        """
        user = self.facebook.current_user
        assert user is not None, 'failed to get current user'
        i_msg = InstantMessage.new(content=content, sender=user.identifier, receiver=receiver)
        return self.send_message(msg=i_msg, callback=callback, split=split)

    def send_message(self, msg: InstantMessage, callback: Callback=None, split: bool=True) -> bool:
        """
        Send instant message (encrypt and sign) onto DIM network

        :param msg:      instant message
        :param callback: callback function
        :param split:    if it's a group message, split it before sending out
        :return:         False on data/delegate error
        """
        facebook = self.facebook
        # Send message (secured + certified) to target station
        s_msg = self.encrypt_message(msg=msg)
        r_msg = self.sign_message(msg=s_msg)
        receiver = facebook.identifier(msg.envelope.receiver)
        ok = True
        if split and receiver.type.is_group():
            # split for each members
            members = facebook.members(identifier=receiver)
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
        handler = MessageCallback(msg=msg, cb=callback)
        data = self.serialize_message(msg=msg)
        return self.delegate.send_package(data=data, handler=handler)

    #
    #   Message
    #
    def forward_message(self, msg: ReliableMessage) -> Optional[Content]:
        """
        Re-pack and deliver (Top-Secret) message to the real receiver

        :param msg: top-secret message
        :return: receipt on success
        """
        receiver = self.facebook.identifier(msg.envelope.receiver)
        secret = ForwardContent.new(message=msg)
        if self.send_content(content=secret, receiver=receiver):
            return ReceiptCommand.new(message='message forwarded')
        else:
            return TextContent.new(text='Sorry, failed to forward your message')

    @abstractmethod
    def broadcast_message(self, msg: ReliableMessage) -> Optional[Content]:
        """
        Deliver message to everyone@everywhere, including all neighbours

        :param msg: broadcast message
        :return: receipt on success
        """
        # NOTICE: this function is for Station
        #         if the receiver is a grouped broadcast ID,
        #         split and deliver to everyone
        pass

    @abstractmethod
    def deliver_message(self, msg: ReliableMessage) -> Optional[Content]:
        """
        Deliver message to the receiver, or broadcast to neighbours

        :param msg: reliable message
        :return: receipt on success
        """
        # NOTICE: this function is for Station
        #         if the station cannot decrypt this message,
        #         it means you should deliver it to the receiver
        pass

    @abstractmethod
    def save_message(self, msg: InstantMessage) -> bool:
        """
        Save instant message

        :param msg: instant message
        :return: True on success
        """
        raise NotImplemented

    @abstractmethod
    def suspend_message(self, msg: Message) -> bool:
        """
        Suspend (instant/reliable)message for the contact's meta

        :param msg: message received from network / instant message to be sent
        :return: False on error
        """
        # NOTICE: this function is for Client
        #         if the client cannot get verify/encrypt message for contact,
        #         it means you should suspend it and query meta from DIM station first
        pass

    #
    #   ConnectionDelegate
    #
    def received_package(self, data: bytes) -> Optional[bytes]:
        """
        Processing received message package

        :param data: message data
        :return: response message data
        """
        # 1. deserialize message
        r_msg = self.deserialize_message(data=data)
        # 2. process message
        response = self.process_message(msg=r_msg)
        if response is None:
            # nothing to response
            return None
        # 3. pack response
        facebook = self.facebook
        user = facebook.current_user
        assert user is not None, 'failed to get current user'
        sender = facebook.identifier(r_msg.envelope.sender)
        i_msg = InstantMessage.new(content=response, sender=user.identifier, receiver=sender)
        s_msg = self.encrypt_message(msg=i_msg)
        msg_r = self.sign_message(msg=s_msg)
        assert msg_r is not None, 'failed to response: %s' % i_msg
        # serialize message
        return self.serialize_message(msg=msg_r)

    # NOTICE: if you want to filter the response, override me
    def process_message(self, msg: ReliableMessage) -> Optional[Content]:
        if self.__processor is None:
            self.__processor = MessageProcessor(messenger=self)
        return self.__processor.process_message(msg=msg)


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
