# -*- coding: utf-8 -*-
from typing import Optional

from mkm import SignKey
from mkm import ID, Profile, Meta
from mkm.immortals import Immortals

from dimsdk import Facebook


class Database(Facebook):

    def __init__(self):
        super().__init__()
        self.__immortals = Immortals()

    def save_meta(self, meta: Meta, identifier: ID) -> bool:
        pass

    def save_profile(self, profile: Profile, identifier: ID = None) -> bool:
        pass

    def load_profile(self, identifier: ID) -> Optional[Profile]:
        pass

    def save_contacts(self, contacts: list, identifier: ID) -> bool:
        pass

    def load_contacts(self, identifier: ID) -> Optional[list]:
        pass

    def save_members(self, members: list, identifier: ID) -> bool:
        pass

    def save_assistants(self, assistants: list, identifier: ID) -> bool:
        pass

    def load_assistants(self, identifier: ID) -> Optional[list]:
        pass

    #
    #   EntityDataSource
    #
    def meta(self, identifier: ID) -> Optional[Meta]:
        return self.__immortals.meta(identifier=identifier)

    #
    #   UserDataSource
    #
    def private_key_for_signature(self, identifier: ID) -> Optional[SignKey]:
        return self.__immortals.private_key_for_signature(identifier=identifier)

    def private_keys_for_decryption(self, identifier: ID) -> Optional[list]:
        return self.__immortals.private_keys_for_decryption(identifier=identifier)
