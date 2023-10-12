# -*- coding: utf-8 -*-
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

from mkm.format import PortableNetworkFile, TransportableData

from .ted import Base64Data, Base64DataFactory
from .pnf import BaseNetworkFile, BaseNetworkFileFactory

from .coder import register_data_coders as register_coders


def register_data_coders():
    register_coders()
    # PNF
    factory = BaseNetworkFileFactory()
    PortableNetworkFile.register(factory=factory)
    # TED
    factory = Base64DataFactory()
    TransportableData.register(algorithm=TransportableData.BASE_64, factory=factory)
    TransportableData.register(algorithm=TransportableData.DEFAULT, factory=factory)
    TransportableData.register(algorithm='*', factory=factory)


__all__ = [

    'Base64Data', 'Base64DataFactory',
    'BaseNetworkFile', 'BaseNetworkFileFactory',

    'register_data_coders',

]
