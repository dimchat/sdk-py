# -*- coding: utf-8 -*-
from typing import Optional, List

from mkm.types import DateTime

from dimsdk import SignKey, DecryptKey
from dimsdk import ID, User, Meta, Document
from dimsdk import Archivist, Facebook


class Database(Archivist):

    def __init__(self):
        super().__init__(expires=Archivist.QUERY_EXPIRES)

    def save_meta(self, meta: Meta, identifier: ID) -> bool:
        pass

    def save_document(self, document: Document) -> bool:
        pass

    def get_last_group_history_time(self, group: ID) -> Optional[DateTime]:
        pass

    def query_meta(self, identifier: ID) -> bool:
        pass

    def query_documents(self, identifier: ID, documents: List[Document]) -> bool:
        pass

    def query_members(self, group: ID, members: List[ID]) -> bool:
        pass

    #
    #   EntityDataSource
    #
    def meta(self, identifier: ID) -> Optional[Meta]:
        pass

    def documents(self, identifier: ID) -> List[Document]:
        return []


g_database = Database()


class CommonFacebook(Facebook):

    @property
    def archivist(self) -> Archivist:
        return g_database

    @property
    def local_users(self) -> List[User]:
        return []

    #
    #   UserDataSource
    #
    def contacts(self, identifier: ID) -> List[ID]:
        return []

    def private_keys_for_decryption(self, identifier: ID) -> List[DecryptKey]:
        return []

    def private_key_for_signature(self, identifier: ID) -> Optional[SignKey]:
        pass

    def private_key_for_visa_signature(self, identifier: ID) -> Optional[SignKey]:
        pass

    #
    #   GroupDataSource
    #
    def assistants(self, identifier: ID) -> List[ID]:
        return []
