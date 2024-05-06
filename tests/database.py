# -*- coding: utf-8 -*-
from typing import Optional, List

from mkm.types import DateTime

from dimsdk import SignKey, DecryptKey
from dimsdk import ID, User, Meta, Document
from dimsdk import Archivist, Facebook


class Database(Archivist):

    def __init__(self):
        super().__init__(expires=Archivist.QUERY_EXPIRES)

    # Override
    async def save_meta(self, meta: Meta, identifier: ID) -> bool:
        pass

    # Override
    async def save_document(self, document: Document) -> bool:
        pass

    # Override
    async def get_last_group_history_time(self, group: ID) -> Optional[DateTime]:
        pass

    # Override
    async def query_meta(self, identifier: ID) -> bool:
        pass

    # Override
    async def query_documents(self, identifier: ID, documents: List[Document]) -> bool:
        pass

    # Override
    async def query_members(self, group: ID, members: List[ID]) -> bool:
        pass

    #
    #   EntityDataSource
    #

    # Override
    async def get_meta(self, identifier: ID) -> Optional[Meta]:
        pass

    # Override
    async def get_documents(self, identifier: ID) -> List[Document]:
        return []


g_database = Database()


class CommonFacebook(Facebook):

    @property  # Override
    def archivist(self) -> Archivist:
        return g_database

    @property  # Override
    async def local_users(self) -> List[User]:
        return []

    #
    #   UserDataSource
    #

    # Override
    async def get_contacts(self, identifier: ID) -> List[ID]:
        return []

    # Override
    async def private_keys_for_decryption(self, identifier: ID) -> List[DecryptKey]:
        return []

    # Override
    async def private_key_for_signature(self, identifier: ID) -> Optional[SignKey]:
        pass

    # Override
    async def private_key_for_visa_signature(self, identifier: ID) -> Optional[SignKey]:
        pass

    #
    #   GroupDataSource
    #

    # Override
    async def get_assistants(self, identifier: ID) -> List[ID]:
        return []
