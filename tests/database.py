# -*- coding: utf-8 -*-
from typing import Optional, List

from dimsdk import Group
from dimsdk import SignKey, DecryptKey
from dimsdk import ID, User, Meta, Document
from dimsdk import Archivist, Barrack, Facebook
from dimsdk import EncryptKey, VerifyKey


class Database(Barrack, Archivist):

    def __init__(self):
        super().__init__()

    # Override
    def cache_user(self, user: User):
        pass

    # Override
    def cache_group(self, group: Group):
        pass

    # Override
    def get_user(self, identifier: ID) -> Optional[User]:
        pass

    # Override
    def get_group(self, identifier: ID) -> Optional[Group]:
        pass

    #
    #   Archivist
    #

    # Override
    async def save_meta(self, meta: Meta, identifier: ID) -> bool:
        return True

    # Override
    async def save_document(self, document: Document) -> bool:
        return True

    # Override
    async def get_meta_key(self, identifier: ID) -> Optional[VerifyKey]:
        pass

    # Override
    async def get_visa_key(self, identifier: ID) -> Optional[EncryptKey]:
        pass

    @property  # Override
    async def local_users(self) -> List[ID]:
        return []


g_database = Database()


class CommonFacebook(Facebook):

    @property  # Override
    def barrack(self) -> Barrack:
        return g_database

    @property  # Override
    def archivist(self) -> Archivist:
        return g_database

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
