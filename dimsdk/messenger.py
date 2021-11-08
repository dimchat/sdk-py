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

from dimp import ID
from dimp import InstantMessage, ReliableMessage
from dimp import Content
from dimp import EntityDelegate
from dimp import Transceiver

from .facebook import Facebook


class Callback:
    """ Messenger Callback """

    @abstractmethod
    def success(self):
        """ Callback on success """
        raise NotImplemented

    @abstractmethod
    def failed(self, error: Exception):
        """ Callback on failed """
        raise NotImplemented


class Messenger(Transceiver):

    def __init__(self):
        super().__init__()
        self.__transmitter: Optional[weakref.ReferenceType] = None
        self.__facebook: Optional[Facebook] = None

    #
    #   Message Transmitter
    #
    class Transmitter:

        @abstractmethod
        def send_content(self, sender: ID, receiver: ID, content: Content,
                         callback: Optional[Callback] = None, priority: int = 0) -> bool:
            """
            Send message content to receiver

            :param sender:   sender ID
            :param receiver: receiver ID
            :param content:  message content
            :param callback: if needs callback, set it here
            :param priority: task priority (smaller is faster)
            :return: True on success
            """
            raise NotImplemented

        @abstractmethod
        def send_instant_message(self, msg: InstantMessage,
                                 callback: Optional[Callback] = None, priority: int = 0) -> bool:
            """
            Send instant message

            :param msg:      instant message
            :param callback: callback function
            :param priority: task priority
            :return:         False on data/delegate error
            """
            raise NotImplemented

        @abstractmethod
        def send_reliable_message(self, msg: ReliableMessage,
                                  callback: Optional[Callback] = None, priority: int = 0) -> bool:
            """
            Send reliable message (encrypt and sign) onto DIM network

            :param msg:      reliable message
            :param callback: callback function
            :param priority: task priority
            :return:         False on data/delegate error
            """
            raise NotImplemented

    #
    #   Delegate for transmitting message
    #
    @property
    def transmitter(self) -> Transmitter:
        if self.__transmitter is not None:
            return self.__transmitter()

    @transmitter.setter
    def transmitter(self, delegate: Transmitter):
        self.__transmitter = weakref.ref(delegate)

    #
    #   Delegate for getting entity
    #
    @property
    def barrack(self) -> EntityDelegate:
        delegate = super().barrack
        if delegate is None:
            delegate = self.facebook
        return delegate

    @barrack.setter
    def barrack(self, delegate: EntityDelegate):
        Transceiver.barrack.__set__(self, delegate)
        if isinstance(delegate, Facebook):
            self.__facebook = delegate

    @property
    def facebook(self) -> Facebook:
        if self.__facebook is None:
            self.__facebook = self._create_facebook()
        return self.__facebook

    @abstractmethod
    def _create_facebook(self) -> Facebook:
        raise NotImplemented

    #
    #   Interfaces for transmitting message
    #
    def send_content(self, sender: Optional[ID], receiver: ID, content: Content,
                     callback: Optional[Callback] = None, priority: int = 0) -> bool:
        return self.transmitter.send_content(sender=sender, receiver=receiver, content=content,
                                             callback=callback, priority=priority)

    def send_instant_message(self, msg: InstantMessage,
                             callback: Optional[Callback] = None, priority: int = 0) -> bool:
        return self.transmitter.send_instant_message(msg=msg, callback=callback, priority=priority)

    def send_reliable_message(self, msg: ReliableMessage,
                              callback: Optional[Callback] = None, priority: int = 0) -> bool:
        return self.transmitter.send_reliable_message(msg=msg, callback=callback, priority=priority)
