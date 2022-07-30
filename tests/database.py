# -*- coding: utf-8 -*-
from typing import Optional, List

from dimsdk import SignKey, DecryptKey
from dimsdk import ID, User, Meta, Document
from dimsdk import Facebook


class Database(Facebook):

    def __init__(self):
        super().__init__()

    @property
    def local_users(self) -> Optional[List[User]]:
        return None

    def save_meta(self, meta: Meta, identifier: ID) -> bool:
        pass

    def save_document(self, document: Document) -> bool:
        pass

    def save_members(self, members: List[ID], identifier: ID) -> bool:
        pass

    #
    #   EntityDataSource
    #
    def meta(self, identifier: ID) -> Optional[Meta]:
        pass

    def document(self, identifier: ID, doc_type: Optional[str] = '*') -> Optional[Document]:
        pass

    #
    #   UserDataSource
    #
    def contacts(self, identifier: ID) -> Optional[List[ID]]:
        pass

    def private_keys_for_decryption(self, identifier: ID) -> Optional[List[DecryptKey]]:
        pass

    def private_key_for_signature(self, identifier: ID) -> Optional[SignKey]:
        pass

    def private_key_for_visa_signature(self, identifier: ID) -> Optional[SignKey]:
        pass

    #
    #   GroupDataSource
    #
    def assistants(self, identifier: ID) -> Optional[List[ID]]:
        pass
