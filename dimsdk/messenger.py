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
from typing import Optional, Union

from mkm.profile import UserProfile
import dkd

from dimp import SymmetricKey, EncryptKey, ID, Meta, User
from dimp import InstantMessage, SecureMessage, ReliableMessage
from dimp import ContentType, Content, FileContent
from dimp import Transceiver

from .delegate import Callback, CompletionHandler
from .delegate import MessengerDelegate
from .facebook import Facebook

from .cpu import ContentProcessor, FileContentProcessor


class Messenger(Transceiver):

    def __init__(self):
        super().__init__()
        self.__context: dict = {}
        self.__delegate: weakref.ReferenceType = None
        self.__cpu = ContentProcessor(messenger=self)

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

    def _select(self, receiver: ID) -> Optional[User]:
        facebook = self.facebook
        users = facebook.local_users
        if users is None or len(users) == 0:
            raise LookupError('local users should not be empty')
        elif receiver.is_broadcast:
            # broadcast message can decrypt by anyone, so just return current user
            return users[0]
        if receiver.is_group:
            # group message (recipient not designated)
            for item in users:
                if facebook.exists_member(member=item.identifier, group=receiver):
                    # set this item to be current user?
                    return item
        else:
            # 1. personal message
            # 2. split group message
            assert receiver.is_user, 'receiver ID error: %s' % receiver
            for item in users:
                if item.identifier == receiver:
                    # set this item to be current user?
                    return item

    def __trim(self, msg: SecureMessage) -> Optional[SecureMessage]:
        # check message delegate
        if msg.delegate is None:
            msg.delegate = self
        receiver = msg.receiver
        user = self._select(receiver=receiver)
        if user is None:
            # current users not match
            msg = None
        elif receiver.is_group:
            # trim group message
            msg = msg.trim(member=user.identifier)
        return msg

    #
    #  Transform
    #
    def verify_message(self, msg: ReliableMessage) -> Optional[SecureMessage]:
        # check message delegate
        if msg.delegate is None:
            msg.delegate = self
        facebook = self.facebook
        sender = msg.sender
        # NOTICE: check meta before calling me
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
        # NOTICE: check profile before calling me
        profile = msg.profile
        if profile is None:
            profile = facebook.profile(identifier=sender)
            if profile is None:
                # NOTICE: the application will query profile automatically
                # save this message in a queue waiting sender's profile response
                self.suspend_message(msg=msg)
                # raise LookupError('failed to get profile for sender: %s' % sender)
                return None
        else:
            # [Profile Protocol]
            # save profile for sender
            profile = UserProfile(profile)
            if not facebook.save_profile(profile=profile, identifier=sender):
                raise ValueError('save profile error: %s, %s' % (sender, profile))
        return super().verify_message(msg=msg)

    def decrypt_message(self, msg: SecureMessage) -> Optional[InstantMessage]:
        # trim message
        s_msg = self.__trim(msg=msg)
        if s_msg is None:
            # not for you?
            raise LookupError('receiver error: %s' % msg)
        # decrypt message
        return super().decrypt_message(msg=s_msg)

    #
    #   InstantMessageDelegate
    #
    def serialize_content(self, content: Content, key: SymmetricKey, msg: InstantMessage) -> bytes:
        # check attachment for File/Image/Audio/Video message content before
        if isinstance(content, FileContent):
            fpu = self.__cpu.cpu(content_type=ContentType.File)
            assert isinstance(fpu, FileContentProcessor), 'FPU error: %s' % fpu
            fpu.upload(content=content, password=key, msg=msg)
        return super().serialize_content(content=content, key=key, msg=msg)

    def encrypt_key(self, data: bytes, receiver: ID, msg: InstantMessage) -> Optional[bytes]:
        facebook = self.facebook
        to = facebook.identifier(receiver)
        pk = facebook.public_key_for_encryption(identifier=to)
        if pk is None:
            meta = facebook.meta(identifier=to)
            if meta is None or not isinstance(meta.key, EncryptKey):
                # save this message in a queue waiting receiver's meta response
                self.suspend_message(msg=msg)
                # raise LookupError('failed to get encrypt key for receiver: %s' % receiver)
                return None
        return super().encrypt_key(data=data, receiver=receiver, msg=msg)

    #
    #   SecureMessageDelegate
    #
    def deserialize_content(self, data: bytes, key: SymmetricKey, msg: SecureMessage) -> Optional[Content]:
        content = super().deserialize_content(data=data, key=key, msg=msg)
        if content is None:
            return None
        # check attachment for File/Image/Audio/Video message content after
        if isinstance(content, FileContent):
            fpu = self.__cpu.cpu(content_type=ContentType.File)
            assert isinstance(fpu, FileContentProcessor), 'FPU error: %s' % fpu
            fpu.download(content=content, password=key, msg=msg)
        return content

    #
    #   Send message
    #
    def send_content(self, content: Content, receiver: ID, callback: Callback=None) -> bool:
        """
        Send content to receiver

        :param content: message content
        :param receiver: receiver ID
        :param callback: callback function
        :return: True on success
        """
        # Application Layer should make sure user is already login before it send message to server.
        # Application layer should put message into queue so that it will send automatically after user login
        user = self.facebook.current_user
        assert user is not None, 'failed to get current user'
        # if receiver.is_group:
        #     if content.group is None:
        #         content.group = receiver
        #     else:
        #         assert receiver == content.group, 'group ID not match: %s, %s' % (receiver, content)
        i_msg = InstantMessage.new(content=content, sender=user.identifier, receiver=receiver)
        return self.send_message(msg=i_msg, callback=callback)

    def send_message(self, msg: Union[InstantMessage, ReliableMessage],
                     callback: Callback=None) -> bool:
        """
        Send instant message (encrypt and sign) onto DIM network

        :param msg:      instant message
        :param callback: callback function
        :return:         False on data/delegate error
        """
        if isinstance(msg, dkd.ReliableMessage):
            return self.__send_message(msg=msg, callback=callback)
        elif not isinstance(msg, dkd.InstantMessage):
            raise TypeError('message error: %s' % msg)

        # Send message (secured + certified) to target station
        s_msg = self.encrypt_message(msg=msg)
        if s_msg is None:
            # public key not found?
            # raise AssertionError('failed to encrypt message: %s' % msg)
            return False
        r_msg = self.sign_message(msg=s_msg)
        if r_msg is None:
            # TODO: set iMsg.state = error
            raise AssertionError('failed to sign message: %s' % s_msg)

        ok = self.__send_message(msg=r_msg, callback=callback)
        # TODO: if OK, set iMsg.state = sending; else set iMsg.state = waiting

        if not self.save_message(msg=msg):
            return False
        return ok

    def __send_message(self, msg: ReliableMessage, callback: Callback) -> bool:
        handler = MessageCallback(msg=msg, cb=callback)
        data = self.serialize_message(msg=msg)
        return self.delegate.send_package(data=data, handler=handler)

    #
    #   Saving Message
    #

    @abstractmethod
    def save_message(self, msg: InstantMessage) -> bool:
        """
        Save instant message

        :param msg: instant message
        :return: True on success
        """
        raise NotImplemented

    @abstractmethod
    def suspend_message(self, msg: Union[ReliableMessage, InstantMessage]):
        """
        Suspend reliable message for the sender's meta
        Suspend instant message for the receiver's meta or group info

        :param msg: message received from network / instant message to be sent
        """
        # NOTICE: this function is for Client
        #         if the client cannot get verify/encrypt message for contact,
        #         it means you should suspend it and query meta from DIM station first
        raise NotImplemented

    #
    #   Process Message Package
    #
    def process_package(self, data: bytes) -> Optional[bytes]:
        """
        Processing received message package

        :param data: message data
        :return: response message data
        """
        # 1. deserialize message
        r_msg = self.deserialize_message(data=data)
        if r_msg is None:
            # no message received
            return None
        # 2. process message
        r_msg = self.process_message(msg=r_msg)
        if r_msg is None:
            # nothing to response
            return None
        # 3. serialize message
        return self.serialize_message(msg=r_msg)

    # TODO: override to check broadcast message before calling it
    # TODO: override to deliver to the receiver when catch exception "receiver error ..."
    def process_message(self, msg: ReliableMessage) -> Optional[ReliableMessage]:
        # 1. verify message
        s_msg = self.verify_message(msg=msg)
        if s_msg is None:
            # waiting for sender's meta if not exists
            return None
        # 2. process message
        s_msg = self.__process_secure(secure=s_msg, msg=msg)
        if s_msg is None:
            # nothing to respond
            return None
        # 3. sign message
        return self.sign_message(msg=s_msg)

    def __process_secure(self, secure: SecureMessage, msg: ReliableMessage) -> Optional[SecureMessage]:
        # 1. decrypt message
        i_msg = self.decrypt_message(msg=secure)
        if i_msg is None:
            # cannot decrypt this message, not for you?
            # delivering message to other receiver?
            return None
        # 2. process message
        i_msg = self.__process_instant(instant=i_msg, msg=msg)
        if i_msg is None:
            # nothing to respond
            return None
        # 3. encrypt message
        return self.encrypt_message(msg=i_msg)

    def __process_instant(self, instant: InstantMessage, msg: ReliableMessage) -> Optional[InstantMessage]:
        # check message delegate
        if instant.delegate is None:
            instant.delegate = self
        sender = instant.sender
        receiver = instant.receiver
        # process content from sender
        res = self.process_content(content=instant.content, sender=sender, msg=msg)
        if not self.save_message(msg=instant):
            # error
            return None
        if res is None:
            # nothing to respond
            return None
        # check receiver
        user = self._select(receiver=receiver)
        assert user is not None, 'receiver error: %s' % receiver
        # pack message
        return InstantMessage.new(content=res, sender=user.identifier, receiver=sender)

    # TODO: override to check group
    # TODO: override to filter the response
    def process_content(self, content: Content, sender: ID, msg: ReliableMessage) -> Optional[Content]:
        # call CPU to process it
        return self.__cpu.process(content=content, sender=sender, msg=msg)


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
