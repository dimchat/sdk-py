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

from abc import abstractmethod
from typing import Optional

from dimp import EntityDelegate
from dimp import Transceiver

from .facebook import Facebook


class Messenger(Transceiver):

    def __init__(self):
        super().__init__()
        self.__facebook: Optional[Facebook] = None

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
