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
    Message Processor
    ~~~~~~~~~~~~~~~~~
"""

import weakref
from typing import Optional

from dimp import ID
from dimp import InstantMessage, ReliableMessage
from dimp import Content, ForwardContent
from dimp import GroupCommand, InviteCommand

from .cpu import ContentProcessor
from .delegate import ConnectionDelegate
from .facebook import Facebook


class MessageProcessor(ConnectionDelegate):

    def __init__(self, messenger):
        super().__init__()
        self.__messenger = weakref.ref(messenger)
        self.__cpu: ContentProcessor = None

    @property
    def messenger(self):  # Messenger
        return self.__messenger()

    @property
    def facebook(self) -> Facebook:
        return self.messenger.facebook

    #
    #   Content Processing Units
    #
    def cpu(self) -> ContentProcessor:
        if self.__cpu is None:
            self.__cpu = ContentProcessor(messenger=self.messenger)
        return self.__cpu

    def __is_empty(self, group: ID) -> bool:
        """
        Check whether group info empty (lost)

        :param group: group ID
        :return: True on members, owner not found
        """
        members = self.facebook.members(identifier=group)
        if members is None or len(members) == 0:
            return True
        owner = self.facebook.owner(identifier=group)
        if owner is None:
            return True

    def __check_group(self, content: Content, sender: ID) -> bool:
        """
        Check if it is a group message, and whether the group members info needs update

        :param content: message content
        :param sender:  message sender
        :return: True on updating
        """
        group = self.facebook.identifier(content.group)
        if group is None or group.is_broadcast:
            # 1. personal message
            # 2. broadcast message
            return False
        # check meta for new group ID
        meta = self.facebook.meta(identifier=group)
        if meta is None:
            # NOTICE: if meta for group not found,
            #         facebook should query it from DIM network automatically
            # TODO: insert the message to a temporary queue to wait meta
            raise LookupError('group meta not found: %s' % group)
        # NOTICE: if the group info not found, and this is not an 'invite' command
        #         query group info from the sender
        needs_update = self.__is_empty(group=group)
        if isinstance(content, InviteCommand):
            # FIXME: can we trust this stranger?
            #        may be we should keep this members list temporary,
            #        and send 'query' to the owner immediately.
            # TODO: check whether the members list is a full list,
            #       it should contain the group owner(owner)
            needs_update = False
        if needs_update:
            query = GroupCommand.query(group=group)
            return self.messenger.send_content(content=query, receiver=sender)

    def __process_message(self, msg: ReliableMessage) -> Optional[Content]:
        messenger = self.messenger
        # verify
        s_msg = messenger.verify_message(msg=msg)
        if s_msg is None:
            raise ValueError('failed to verify message: %s' % msg)
        receiver = self.facebook.identifier(msg.envelope.receiver)
        #
        #  1. check broadcast
        #
        if receiver.type.is_group() and receiver.is_broadcast:
            # if it's a grouped broadcast id, then split and deliver to everyone
            return messenger.broadcast_message(msg=msg)
        #
        #  2. try to decrypt
        #
        i_msg = messenger.decrypt_message(msg=s_msg)
        if i_msg is None:
            # cannot decrypt this message, not for you?
            # deliver to the receiver
            return messenger.deliver_message(msg=msg)
        #
        #  3. check top-secret message
        #
        content = i_msg.content
        if isinstance(content, ForwardContent):
            # it's asking you to forward it
            return messenger.forward_message(msg=content.forward)
        #
        #  4. check group
        #
        sender = self.facebook.identifier(msg.envelope.sender)
        if self.__check_group(content=content, sender=sender):
            pass
        #
        #  5. process
        #
        response = self.cpu().process(content=content, sender=sender, msg=i_msg)
        if messenger.save_message(msg=i_msg):
            return response

    #
    #   ConnectionDelegate
    #
    def received_package(self, data: bytes) -> Optional[bytes]:
        """
        Processing received message package

        :param data: message data
        :return: response message data
        """
        messenger = self.messenger
        r_msg = messenger.deserialize_message(data=data)
        response = self.__process_message(msg=r_msg)
        if response is None:
            # nothing to response
            return None
        # response to the sender
        user = messenger.current_user
        assert user is not None, 'failed to get current user'
        sender = self.facebook.identifier(r_msg.envelope.sender)
        i_msg = InstantMessage.new(content=response, sender=user.identifier, receiver=sender)
        s_msg = messenger.encrypt_message(msg=i_msg)
        msg_r = messenger.sign_message(msg=s_msg)
        assert msg_r is not None, 'failed to response: %s' % i_msg
        return messenger.serialize_message(msg=msg_r)
