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
    Delegates
    ~~~~~~~~~

    Delegates for Messenger
"""

from abc import ABCMeta, abstractmethod
from typing import Optional

from dimp import InstantMessage


class Callback(metaclass=ABCMeta):

    @abstractmethod
    def finished(self, result, error=None):
        pass


class CompletionHandler(metaclass=ABCMeta):

    @abstractmethod
    def success(self):
        pass

    @abstractmethod
    def failed(self, error):
        pass


class MessengerDelegate(metaclass=ABCMeta):

    @abstractmethod
    def upload_data(self, data: bytes, msg: InstantMessage) -> str:
        """
        Upload encrypted data to CDN

        :param data: encrypted file data
        :param msg:  instant message
        :return: download URL
        """
        pass

    @abstractmethod
    def download_data(self, url: str, msg: InstantMessage) -> Optional[bytes]:
        """
        Download encrypted data from CDN

        :param url: download URL
        :param msg: instant message
        :return: encrypted file data
        """
        pass

    @abstractmethod
    def send_package(self, data: bytes, handler: CompletionHandler) -> bool:
        """
        Send out a data package onto network

        :param data:    package data
        :param handler: completion handler
        :return: False on data/delegate error
        """
        pass


class ConnectionDelegate(metaclass=ABCMeta):

    @abstractmethod
    def received_package(self, data: bytes) -> Optional[bytes]:
        """ Receive data package

        :param data: data package
        :return: response to sender
        """
        pass
