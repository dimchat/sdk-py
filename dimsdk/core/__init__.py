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

from .barrack import Barrack

from .packer import Packer
from .processor import Processor
from .transformer import Transformer

from .delegate import CipherKeyDelegate

#
#   Dao-Ke-Dao (shortener / compressor)
#   NOTE: physically located in `dkd/`; re-exported here to match the Dart
#         barrel (lib/core.dart exports src/dkd/compress_keys.dart & compressor.dart)
#
from ..dkd.compress_keys import Shortener, MessageShortener
from ..dkd.compressor import Compressor, MessageCompressor


__all__ = [

    #
    #   Core Interfaces
    #

    'Barrack',

    'Packer',
    'Processor',
    'Transformer',

    'CipherKeyDelegate',

    'Shortener', 'MessageShortener',
    'Compressor', 'MessageCompressor',

]
