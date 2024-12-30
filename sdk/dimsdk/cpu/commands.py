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

from ..mkm import MetaUtils, DocumentUtils

from .base import BaseCommandProcessor


class MetaCommandProcessor(BaseCommandProcessor):
    """
        Meta Command Processor
        ~~~~~~~~~~~~~~~~~~~~~~

    """

    # Override
    async def process_content(self, content: Content, r_msg: ReliableMessage) -> List[Content]:
        assert isinstance(content, MetaCommand), 'meta command error: %s' % content
        identifier = content.identifier
        meta = content.meta
        if meta is None:
            # query meta for ID
            return await self._get_meta(identifier=identifier, content=content, envelope=r_msg.envelope)
        else:
            # received a meta for ID
            return await self._put_meta(meta=meta, identifier=identifier, content=content, envelope=r_msg.envelope)

    # private
    async def _get_meta(self, identifier: ID, content: MetaCommand, envelope: Envelope) -> List[Content]:
        meta = await self.facebook.get_meta(identifier=identifier)
        if meta is None:
            text = 'Meta not found.'
            return self._respond_receipt(text=text, content=content, envelope=envelope, extra={
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
    async def _put_meta(self, meta: Meta, identifier: ID, content: MetaCommand, envelope: Envelope) -> List[Content]:
        # 1. try to save meta
        errors = await self._save_meta(identifier=identifier, meta=meta, content=content, envelope=envelope)
        if errors is not None:
            # failed
            return errors
        # 2. success
        text = 'Meta received.'
        return self._respond_receipt(text=text, content=content, envelope=envelope, extra={
            'template': 'Meta received: ${ID}.',
            'replacements': {
                'ID': str(identifier),
            }
        })

    # protected
    async def _save_meta(self, meta: Meta, identifier: ID,
                         content: MetaCommand, envelope: Envelope) -> Optional[List[Content]]:
        # check meta
        if not await self._check_meta(meta=meta, identifier=identifier):
            text = 'Meta not valid.'
            return self._respond_receipt(text=text, content=content, envelope=envelope, extra={
                'template': 'Meta not valid: ${ID}.',
                'replacements': {
                    'ID': str(identifier),
                }
            })
        elif not await self.facebook.save_meta(meta=meta, identifier=identifier):
            text = 'Meta not accepted.'
            return self._respond_receipt(text=text, content=content, envelope=envelope, extra={
                'template': 'Meta not accepted: ${ID}.',
                'replacements': {
                    'ID': str(identifier),
                }
            })
        # meta saved, return no error

    # noinspection PyMethodMayBeStatic
    async def _check_meta(self, meta: Meta, identifier: ID) -> bool:
        return meta.valid and MetaUtils.match_identifier(identifier=identifier, meta=meta)


class DocumentCommandProcessor(MetaCommandProcessor):
    """
        Document Command Processor
        ~~~~~~~~~~~~~~~~~~~~~~~~~~

    """

    # Override
    async def process_content(self, content: Content, r_msg: ReliableMessage) -> List[Content]:
        assert isinstance(content, DocumentCommand), 'document command error: %s' % content
        identifier = content.identifier
        doc = content.document
        if doc is None:
            # query entity document for ID
            return await self._get_documents(identifier=identifier, content=content, envelope=r_msg.envelope)
        elif identifier == doc.identifier:
            # received a document for ID
            return await self._put_doc(doc, identifier=identifier, content=content, envelope=r_msg.envelope)
        # error
        text = 'Document ID not match.'
        return self._respond_receipt(text=text, content=content, envelope=r_msg.envelope, extra={
            'template': 'Document ID not match: ${ID}.',
            'replacements': {
                'ID': str(identifier),
            }
        })

    # private
    async def _get_documents(self, identifier: ID, content: DocumentCommand, envelope: Envelope) -> List[Content]:
        facebook = self.facebook
        documents = await facebook.get_documents(identifier=identifier)
        count = 0 if documents is None else len(documents)
        if count == 0:
            text = 'Document not found.'
            return self._respond_receipt(text=text, content=content, envelope=envelope, extra={
                'template': 'Document not found: ${ID}.',
                'replacements': {
                    'ID': str(identifier),
                }
            })
        # document got
        query_time = content.last_time
        if query_time is not None:
            # check last document time
            last = DocumentUtils.last_document(documents=documents)
            assert last is not None, 'should not happen'
            last_time = last.time
            if last_time is None:
                assert False, 'document error: %s' % last
                pass
            elif not last_time.after(query_time):
                # document not updated
                text = 'Document not updated.'
                return self._respond_receipt(text=text, content=content, envelope=envelope, extra={
                    'template': 'Document not updated: ${ID}, last time: ${time}.',
                    'replacements': {
                        'ID': str(identifier),
                        'time': last_time.timestamp,
                    }
                })
        meta = await facebook.get_meta(identifier=identifier)
        # respond first document with meta
        command = DocumentCommand.response(identifier=identifier, meta=meta, document=documents[0])
        responses = [command]
        for i in range(1, count):
            # respond other documents
            command = DocumentCommand.response(identifier=identifier, meta=meta, document=documents[i])
            responses.append(command)
        return responses

    # private
    async def _put_doc(self, doc: Document, identifier: ID,
                       content: DocumentCommand, envelope: Envelope) -> List[Content]:
        facebook = self.facebook
        meta = content.meta
        # 0. check meta
        if meta is None:
            meta = await facebook.get_meta(identifier=identifier)
            if meta is None:
                text = 'Meta not found.'
                return self._respond_receipt(text=text, content=content, envelope=envelope, extra={
                    'template': 'Meta not found: ${ID}.',
                    'replacements': {
                        'ID': str(identifier),
                    }
                })
        else:
            # 1. try to save meta
            errors = await self._save_meta(meta=meta, identifier=identifier, content=content, envelope=envelope)
            if errors is not None:
                # failed
                return errors
        # 2. try to save document
        errors = await self._save_document(doc, meta=meta, identifier=identifier, content=content, envelope=envelope)
        if errors is not None:
            # failed
            return errors
        # 3. success
        text = 'Document received.'
        return self._respond_receipt(text=text, content=content, envelope=envelope, extra={
            'template': 'Document received: ${ID}.',
            'replacements': {
                'ID': str(identifier),
            }
        })

    # protected
    async def _save_document(self, doc: Document, meta: Meta, identifier: ID,
                             content: DocumentCommand, envelope: Envelope) -> Optional[List[Content]]:
        # check document
        if not await self._check_document(doc, meta=meta):
            # document error
            text = 'Document not accepted.'
            return self._respond_receipt(text=text, content=content, envelope=envelope, extra={
                'template': 'Document not accepted: ${ID}.',
                'replacements': {
                    'ID': str(identifier),
                }
            })
        elif not await self.facebook.save_document(document=doc):
            # document expired
            text = 'Document not changed.'
            return self._respond_receipt(text=text, content=content, envelope=envelope, extra={
                'template': 'Document not changed: ${ID}.',
                'replacements': {
                    'ID': str(identifier),
                }
            })
        # document saved, return no error

    # noinspection PyMethodMayBeStatic
    async def _check_document(self, doc: Document, meta: Meta) -> bool:
        if doc.valid:
            return True
        # NOTICE: if this is a bulletin document for group,
        #             verify it with the group owner's meta.key
        #         else (this is a visa document for user)
        #             verify it with the user's meta.key
        return doc.verify(public_key=meta.public_key)
        # TODO: check for group document
