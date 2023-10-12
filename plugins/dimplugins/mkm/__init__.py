# -*- coding: utf-8 -*-
#
#   Ming-Ke-Ming : Decentralized User Identity Authentication
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

from .btc import BTCAddress
from .eth import ETHAddress

from .address import BaseAddressFactory, GeneralAddressFactory
from .identifier import GeneralIdentifierFactory

from .meta import DefaultMeta, BTCMeta, ETHMeta, GeneralMetaFactory
from .docs import GeneralDocumentFactory

from .address import register_address_factory
from .identifier import register_identifier_factory
from .meta import register_meta_factories
from .docs import register_document_factories


__all__ = [

    'BTCAddress', 'ETHAddress',
    'DefaultMeta', 'BTCMeta', 'ETHMeta',

    'BaseAddressFactory', 'GeneralAddressFactory',
    'GeneralIdentifierFactory',
    'GeneralMetaFactory',
    'GeneralDocumentFactory',

    'register_address_factory',
    'register_identifier_factory',
    'register_meta_factories',
    'register_document_factories',

]
