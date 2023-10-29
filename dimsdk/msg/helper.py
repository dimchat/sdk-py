# -*- coding: utf-8 -*-
#
#   DIMP : Decentralized Instant Messaging Protocol
#
#                                Written in 2023 by Moky <albert.moky@gmail.com>
#
# ==============================================================================
# MIT License
#
# Copyright (c) 2023 Albert Moky
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

from abc import ABC
from typing import Optional

from dimp import Meta, Visa, Document
from dimp import ReliableMessage


class MessageHelper(ABC):

    """
        Sender's Meta
        ~~~~~~~~~~~~~
        Extends for the first message package of 'Handshake' protocol.
    """

    @classmethod
    def get_meta(cls, msg: ReliableMessage) -> Optional[Meta]:
        meta = msg.get('meta')
        return Meta.parse(meta=meta)

    @classmethod
    def set_meta(cls, meta: Meta, msg: ReliableMessage):
        msg.set_map(key='meta', value=meta)

    """
        Sender's Visa
        ~~~~~~~~~~~~~
        Extends for the first message package of 'Handshake' protocol.
    """

    @classmethod
    def get_visa(cls, msg: ReliableMessage) -> Optional[Visa]:
        visa = msg.get('visa')
        doc = Document.parse(document=visa)
        if isinstance(doc, Visa):
            return doc
        assert doc is None, 'visa document error: %s' % visa

    @classmethod
    def set_visa(cls, visa: Visa, msg: ReliableMessage):
        msg.set_map(key='visa', value=visa)
