# -*- coding: utf-8 -*-
from typing import Optional, List

from dimsdk import DateTime, Group
from dimsdk import SignKey, DecryptKey
from dimsdk import ID, User, Meta, Document
from dimsdk import Archivist, Facebook
from mkm.crypto import EncryptKey, VerifyKey


class Database(Archivist):

    def __init__(self):
        super().__init__()

    # Override
    async def create_user(self, identifier: ID) -> Optional[User]:
        pass

    # Override
    async def create_group(self, identifier: ID) -> Optional[Group]:
        pass

    @property  # Override
    async def local_users(self) -> List[User]:
        return []

    # Override
    async def get_meta_key(self, identifier: ID) -> Optional[VerifyKey]:
        pass

    # Override
    async def get_visa_key(self, identifier: ID) -> Optional[EncryptKey]:
        pass


g_database = Database()


class CommonFacebook(Facebook):

    @property  # Override
    def archivist(self) -> Archivist:
        return g_database

    # Override
    async def save_meta(self, meta: Meta, identifier: ID) -> bool:
        pass

    # Override
    async def save_document(self, document: Document) -> bool:
        pass

    #
    #   EntityDataSource
    #

    # Override
    async def get_meta(self, identifier: ID) -> Optional[Meta]:
        pass

    # Override
    async def get_documents(self, identifier: ID) -> List[Document]:
        pass

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
    async def get_founder(self, identifier: ID) -> Optional[ID]:
        pass

    # Override
    async def get_owner(self, identifier: ID) -> Optional[ID]:
        pass

    # Override
    async def get_members(self, identifier: ID) -> List[ID]:
        pass

    # Override
    async def get_assistants(self, identifier: ID) -> List[ID]:
        return []
