# -*- coding: utf-8 -*-
#
#   DIM-SDK : Decentralized Instant Messaging Software Development Kit
#
#                                Written in 2024 by Moky <albert.moky@gmail.com>
#
# ==============================================================================
# MIT License
#
# Copyright (c) 2024 Albert Moky
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

from typing import Optional, List

from dimp import utf8_encode
from dimp import DateTime

from dimp import VerifyKey

from dimp import Address, ID, Meta
from dimp import Document, Visa, Bulletin


class MetaUtils:

    @classmethod
    def match_identifier(cls, identifier: ID, meta: Meta) -> bool:
        assert meta.valid, 'meta not valid: %s' % meta
        # check ID.name
        seed = meta.seed
        name = identifier.name
        if name is None or len(name) == 0:
            if seed is not None and len(seed) > 0:
                return False
        elif name != seed:
            return False
        # check ID.address
        old = identifier.address
        gen = Address.generate(meta=meta, network=old.network)
        return old == gen

    @classmethod
    def match_public_key(cls, key: VerifyKey, meta: Meta) -> bool:
        assert meta.valid, 'meta not valid: %s' % meta
        # check whether the public key equals to meta.key
        if key == meta.public_key:
            return True
        # check with seed & fingerprint
        seed = meta.seed
        if seed is None or len(seed) == 0:
            # NOTICE: ID with BTC/ETH address has no username, so
            #         just compare the key.data to check matching
            return False
        fingerprint = meta.fingerprint
        if fingerprint is None or len(fingerprint) == 0:
            # fingerprint should not be empty here
            return False
        # check whether keys equal by verifying signature
        data = utf8_encode(string=seed)
        return key.verify(data=data, signature=fingerprint)


class DocumentUtils:

    @classmethod
    def is_before(cls, old_time: Optional[DateTime], this_time: Optional[DateTime]) -> bool:
        """ Check whether this time is before old time """
        if old_time is not None and this_time is not None:
            return this_time.before(old_time)

    @classmethod
    def is_expired(cls, this_doc: Document, old_doc: Document) -> bool:
        """ Check whether this document's time is before old document's time """
        return cls.is_before(old_time=old_doc.time, this_time=this_doc.time)

    @classmethod
    def last_document(cls, documents: List[Document], doc_type: str = None) -> Optional[Document]:
        """ Select last document matched the type """
        if documents is None or len(documents) == 0:
            return None
        elif doc_type is None or doc_type == '*':
            doc_type = ''
        check_type = len(doc_type) > 0
        last: Optional[Document] = None
        for item in documents:
            # 1. check type
            if check_type:
                item_type = item.type
                if item_type is not None and len(item_type) > 0 and item_type != doc_type:
                    # type not matched, skip it
                    continue
            # 2. check time
            if last is not None and cls.is_expired(this_doc=item, old_doc=last):
                # skip expired document
                continue
            # got it
            last = item
        return last

    @classmethod
    def last_visa(cls, documents: List[Document]) -> Optional[Visa]:
        """ Select last visa document """
        if documents is None or len(documents) == 0:
            return None
        last: Optional[Visa] = None
        for item in documents:
            # 1. check type
            if not isinstance(item, Visa):
                # type not matched, skip it
                continue
            # 2. check time
            if last is not None and cls.is_expired(this_doc=item, old_doc=last):
                # skip expired document
                continue
            # got it
            last = item
        return last

    @classmethod
    def last_bulletin(cls, documents: List[Document]) -> Optional[Bulletin]:
        """ Select last bulletin document """
        if documents is None or len(documents) == 0:
            return None
        last: Optional[Bulletin] = None
        for item in documents:
            # 1. check type
            if not isinstance(item, Bulletin):
                # type not matched, skip it
                continue
            # 2. check time
            if last is not None and cls.is_expired(this_doc=item, old_doc=last):
                # skip expired document
                continue
            # got it
            last = item
        return last
