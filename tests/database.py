# -*- coding: utf-8 -*-
from typing import Optional

from dimp import SignKey
from dimp import ID, Meta, Document

from dimsdk import Facebook
from dimsdk.immortals import Immortals


class Database(Facebook):

    def __init__(self):
        super().__init__()
        self.__immortals = Immortals()

    def local_users(self) -> Optional[list]:
        pass

    def save_meta(self, meta: Meta, identifier: ID) -> bool:
        pass

    def save_document(self, document: Document) -> bool:
        pass

    def save_members(self, members: list, identifier: ID) -> bool:
        pass

    #
    #   EntityDataSource
    #
    def meta(self, identifier: ID) -> Optional[Meta]:
        return self.__immortals.meta(identifier=identifier)

    def document(self, identifier: ID, doc_type: Optional[str] = '*') -> Optional[Document]:
        return self.__immortals.document(identifier=identifier)

    #
    #   UserDataSource
    #
    def contacts(self, identifier: ID) -> Optional[list]:
        pass

    def private_keys_for_decryption(self, identifier: ID) -> Optional[list]:
        return self.__immortals.private_keys_for_decryption(identifier=identifier)

    def private_key_for_signature(self, identifier: ID) -> Optional[SignKey]:
        return self.__immortals.private_key_for_signature(identifier=identifier)

    def private_key_for_visa_signature(self, identifier: ID) -> Optional[SignKey]:
        return self.__immortals.private_key_for_visa_signature(identifier=identifier)

    #
    #   GroupDataSource
    #
    def assistants(self, identifier: ID) -> Optional[list]:
        pass
