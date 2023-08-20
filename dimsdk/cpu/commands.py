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


from typing import Optional, List

from dimp import ID, Meta, Document
from dimp import ReliableMessage
from dimp import Content
from dimp import MetaCommand, DocumentCommand, ReceiptCommand

from .base import BaseCommandProcessor


def get_facebook(cpu: BaseCommandProcessor):  # -> Facebook:
    facebook = cpu.facebook
    from ..facebook import Facebook
    assert isinstance(facebook, Facebook), 'facebook error: %s' % facebook
    return facebook


class MetaCommandProcessor(BaseCommandProcessor):
    """
        Meta Command Processor
        ~~~~~~~~~~~~~~~~~~~~~~

    """

    # Override
    def process_content(self, content: Content, r_msg: ReliableMessage) -> List[Content]:
        assert isinstance(content, MetaCommand), 'meta command error: %s' % content
        identifier = content.identifier
        meta = content.meta
        if meta is None:
            # query meta for ID
            return self._get_meta(identifier=identifier, msg=r_msg)
        else:
            # received a meta for ID
            return self._put_meta(identifier=identifier, meta=meta, msg=r_msg)

    def _get_meta(self, identifier: ID, msg: ReliableMessage) -> List[Content]:
        facebook = get_facebook(cpu=self)
        meta = facebook.meta(identifier=identifier)
        if meta is None:
            return self._respond_receipt(text='Meta not found.', msg=msg, extra={
                'template': 'Meta not found: ${ID}.',
                'replacements': {
                    'ID': str(identifier),
                }
            })
        else:
            res = MetaCommand.response(identifier=identifier, meta=meta)
            return [res]

    def _put_meta(self, identifier: ID, meta: Meta, msg: ReliableMessage) -> List[Content]:
        facebook = get_facebook(cpu=self)
        if facebook.save_meta(meta=meta, identifier=identifier):
            return self._respond_receipt(text='Meta received.', msg=msg, extra={
                'template': 'Meta received: ${ID}.',
                'replacements': {
                    'ID': str(identifier),
                }
            })
        else:
            return self._respond_receipt(text='Meta not accepted.', msg=msg, extra={
                'template': 'Meta not accepted: ${ID}.',
                'replacements': {
                    'ID': str(identifier),
                }
            })


class DocumentCommandProcessor(MetaCommandProcessor):
    """
        Document Command Processor
        ~~~~~~~~~~~~~~~~~~~~~~~~~~

    """

    # Override
    def process_content(self, content: Content, r_msg: ReliableMessage) -> List[Content]:
        assert isinstance(content, DocumentCommand), 'document command error: %s' % content
        identifier = content.identifier
        doc = content.document
        if doc is None:
            # query entity document for ID
            doc_type = content.get_str(key='doc_type', default='*')
            return self._get_doc(identifier=identifier, doc_type=doc_type, msg=r_msg)
        else:
            # received a new document for ID
            return self._put_doc(identifier=identifier, meta=content.meta, document=doc, msg=r_msg)

    def _get_doc(self, identifier: ID, doc_type: str, msg: ReliableMessage) -> List[Content]:
        facebook = get_facebook(cpu=self)
        doc = facebook.document(identifier=identifier, doc_type=doc_type)
        if doc is None:
            return self._respond_receipt(text='Document not found.', msg=msg, extra={
                'template': 'Document not found: ${ID}.',
                'replacements': {
                    'ID': str(identifier),
                }
            })
        else:
            meta = facebook.meta(identifier=identifier)
            res = DocumentCommand.response(document=doc, meta=meta, identifier=identifier)
            return [res]

    def _put_doc(self, identifier: ID, meta: Optional[Meta], document: Document, msg: ReliableMessage) -> List[Content]:
        facebook = get_facebook(cpu=self)
        # check meta
        if meta is None:
            meta = facebook.meta(identifier=identifier)
            if meta is None:
                return self._respond_receipt(text='Meta not found.', msg=msg, extra={
                    'template': 'Meta not found: ${ID}.',
                    'replacements': {
                        'ID': str(identifier),
                    }
                })
        elif not facebook.save_meta(meta=meta, identifier=identifier):
            return self._respond_receipt(text='Meta not accepted.', msg=msg, extra={
                'template': 'Meta not accepted: ${ID}.',
                'replacements': {
                    'ID': str(identifier),
                }
            })
        # check document
        valid = document.valid or document.verify(public_key=meta.key)
        # TODO: check for group document
        if not valid:
            # document error
            return self._respond_receipt(text='Document not accepted.', msg=msg, extra={
                'template': 'Document not accepted: ${ID}.',
                'replacements': {
                    'ID': str(identifier),
                }
            })
        elif facebook.save_document(document=document):
            # document saved
            return self._respond_receipt(text='Document received.', msg=msg, extra={
                'template': 'Document received: ${ID}.',
                'replacements': {
                    'ID': str(identifier),
                }
            })
        # document expired
        return self._respond_receipt(text='Document not changed.', msg=msg, extra={
            'template': 'Document not changed: ${ID}.',
            'replacements': {
                'ID': str(identifier),
            }
        })


class ReceiptCommandProcessor(BaseCommandProcessor):

    # Override
    def process_content(self, content: Content, r_msg: ReliableMessage) -> List[Content]:
        assert isinstance(content, ReceiptCommand), 'receipt command error: %s' % content
        # no need to response login command
        return []
