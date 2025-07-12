# -*- coding: utf-8 -*-
#
#   Ming-Ke-Ming : Decentralized User Identity Authentication
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

from typing import Optional, Dict

from dimp import TransportableData
from dimp import ID
from dimp import DocumentType
from dimp import Document, DocumentFactory
from dimp import BaseDocument, BaseVisa, BaseBulletin
from dimp.plugins import SharedAccountExtensions


class GeneralDocumentFactory(DocumentFactory):
    """ General Document Factory """

    def __init__(self, doc_type: str):
        super().__init__()
        self.__type = doc_type

    @property  # protected
    def type(self) -> str:
        return self.__type

    # Override
    def create_document(self, identifier: ID, data: Optional[str], signature: Optional[TransportableData]) -> Document:
        doc_type = get_doc_type(doc_type=self.type, identifier=identifier)
        if data is None or len(data) == 0:
            assert signature is None, 'document error: %s, signature: %s' % (identifier, signature)
            # create emtpy document
            if doc_type == DocumentType.VISA:
                return BaseVisa(identifier=identifier)
            elif doc_type == DocumentType.BULLETIN:
                return BaseBulletin(identifier=identifier)
            else:
                return BaseDocument(doc_type=doc_type, identifier=identifier)
        else:
            assert signature is not None, 'document error: %s, data: %s' % (identifier, data)
            # create document with data & signature from local storage
            if doc_type == DocumentType.VISA:
                return BaseVisa(identifier=identifier, data=data, signature=signature)
            elif doc_type == DocumentType.BULLETIN:
                return BaseBulletin(identifier=identifier, data=data, signature=signature)
            else:
                return BaseDocument(doc_type=doc_type, identifier=identifier, data=data, signature=signature)

    # Override
    def parse_document(self, document: Dict) -> Optional[Document]:
        # check 'did', 'data', 'signature'
        identifier = ID.parse(identifier=document.get('did'))
        if identifier is None:
            # assert False, 'document ID not found: %s' % document
            return None
        elif document.get('data') is None or document.get('signature') is None:
            # document.data should not be empty
            # document.signature should not be empty
            return None
        # check document type
        ext = SharedAccountExtensions()
        doc_type = ext.helper.get_document_type(document=document, default=None)
        if doc_type is None:
            doc_type = get_doc_type(doc_type='*', identifier=identifier)
        # create with document type
        if doc_type == DocumentType.VISA:
            return BaseVisa(document=document)
        elif doc_type == DocumentType.BULLETIN:
            return BaseBulletin(document=document)
        else:
            return BaseDocument(document=document)


def get_doc_type(doc_type: str, identifier: ID) -> str:
    assert doc_type is not None and len(doc_type) > 0, 'document type empty'
    if doc_type != '*':
        return doc_type
    elif identifier.is_group:
        return DocumentType.BULLETIN
    elif identifier.is_user:
        return DocumentType.VISA
    else:
        return DocumentType.PROFILE
