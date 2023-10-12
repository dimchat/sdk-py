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
from dimp import Envelope, Content
from dimp import MetaCommand, DocumentCommand

from .base import BaseCommandProcessor


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
            return self._get_meta(identifier=identifier, content=content, envelope=r_msg.envelope)
        else:
            # received a meta for ID
            return self._put_meta(meta=meta, identifier=identifier, content=content, envelope=r_msg.envelope)

    # private
    def _get_meta(self, identifier: ID, content: MetaCommand, envelope: Envelope) -> List[Content]:
        meta = self.facebook.meta(identifier=identifier)
        if meta is None:
            text = 'Meta not found.'
            return self.respond_receipt(text=text, content=content, envelope=envelope, extra={
                'template': 'Meta not found: ${ID}.',
                'replacements': {
                    'ID': str(identifier),
                }
            })
        # meta got
        return [
            MetaCommand.response(identifier=identifier, meta=meta)
        ]

    # private
    def _put_meta(self, meta: Meta, identifier: ID, content: MetaCommand, envelope: Envelope) -> List[Content]:
        # 1. try to save meta
        errors = self._save_meta(identifier=identifier, meta=meta, content=content, envelope=envelope)
        if errors is not None:
            # failed
            return errors
        # 2. success
        text = 'Meta received.'
        return self.respond_receipt(text=text, content=content, envelope=envelope, extra={
            'template': 'Meta received: ${ID}.',
            'replacements': {
                'ID': str(identifier),
            }
        })

    # protected
    def _save_meta(self, meta: Meta, identifier: ID,
                   content: MetaCommand, envelope: Envelope) -> Optional[List[Content]]:
        # check meta
        if not self._check_meta(meta=meta, identifier=identifier):
            text = 'Meta not valid.'
            return self.respond_receipt(text=text, content=content, envelope=envelope, extra={
                'template': 'Meta not valid: ${ID}.',
                'replacements': {
                    'ID': str(identifier),
                }
            })
        elif not self.facebook.save_meta(meta=meta, identifier=identifier):
            text = 'Meta not accepted.'
            return self.respond_receipt(text=text, content=content, envelope=envelope, extra={
                'template': 'Meta not accepted: ${ID}.',
                'replacements': {
                    'ID': str(identifier),
                }
            })
        # meta saved, return no error

    # noinspection PyMethodMayBeStatic
    def _check_meta(self, meta: Meta, identifier: ID) -> bool:
        return meta.valid and meta.match_identifier(identifier=identifier)


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
            return self._get_doc(identifier=identifier, doc_type=doc_type, content=content, envelope=r_msg.envelope)
        elif identifier == doc.identifier:
            # received a document for ID
            return self._put_doc(doc, identifier=identifier, content=content, envelope=r_msg.envelope)
        # error
        text = 'Document ID not match.'
        return self.respond_receipt(text=text, content=content, envelope=r_msg.envelope, extra={
            'template': 'Document ID not match: ${ID}.',
            'replacements': {
                'ID': str(identifier),
            }
        })

    # private
    def _get_doc(self, identifier: ID, doc_type: str, content: DocumentCommand, envelope: Envelope) -> List[Content]:
        facebook = self.facebook
        doc = facebook.document(identifier=identifier, doc_type=doc_type)
        if doc is None:
            text = 'Document not found.'
            return self.respond_receipt(text=text, content=content, envelope=envelope, extra={
                'template': 'Document not found: ${ID}.',
                'replacements': {
                    'ID': str(identifier),
                }
            })
        # document got
        meta = facebook.meta(identifier=identifier)
        return [
            DocumentCommand.response(document=doc, meta=meta, identifier=identifier)
        ]

    # private
    def _put_doc(self, doc: Document, identifier: ID, content: DocumentCommand, envelope: Envelope) -> List[Content]:
        facebook = self.facebook
        meta = content.meta
        # 0. check meta
        if meta is None:
            meta = facebook.meta(identifier=identifier)
            if meta is None:
                text = 'Meta not found.'
                return self.respond_receipt(text=text, content=content, envelope=envelope, extra={
                    'template': 'Meta not found: ${ID}.',
                    'replacements': {
                        'ID': str(identifier),
                    }
                })
        else:
            # 1. try to save meta
            errors = self._save_meta(meta=meta, identifier=identifier, content=content, envelope=envelope)
            if errors is not None:
                # failed
                return errors
        # 2. try to save document
        errors = self._save_document(doc, meta=meta, identifier=identifier, content=content, envelope=envelope)
        if errors is not None:
            # failed
            return errors
        # 3. success
        text = 'Document received.'
        return self.respond_receipt(text=text, content=content, envelope=envelope, extra={
            'template': 'Document received: ${ID}.',
            'replacements': {
                'ID': str(identifier),
            }
        })

    # protected
    def _save_document(self, doc: Document, meta: Meta, identifier: ID,
                       content: DocumentCommand, envelope: Envelope) -> Optional[List[Content]]:
        # check document
        if not self._check_document(doc, meta=meta):
            # document error
            text = 'Document not accepted.'
            return self.respond_receipt(text=text, content=content, envelope=envelope, extra={
                'template': 'Document not accepted: ${ID}.',
                'replacements': {
                    'ID': str(identifier),
                }
            })
        elif not self.facebook.save_document(document=doc):
            # document expired
            text = 'Document not changed.'
            return self.respond_receipt(text=text, content=content, envelope=envelope, extra={
                'template': 'Document not changed: ${ID}.',
                'replacements': {
                    'ID': str(identifier),
                }
            })
        # document saved, return no error

    # noinspection PyMethodMayBeStatic
    def _check_document(self, doc: Document, meta: Meta) -> bool:
        if doc.valid:
            return True
        # NOTICE: if this is a bulletin document for group,
        #             verify it with the group owner's meta.key
        #         else (this is a visa document for user)
        #             verify it with the user's meta.key
        return doc.verify(public_key=meta.public_key)
        # TODO: check for group document
