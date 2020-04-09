# -*- coding: utf-8 -*-
from typing import Optional

from dimp import SignKey
from dimp import ID, Profile, Meta

from dimsdk import Facebook
from dimsdk.immortals import Immortals


class Database(Facebook):

    def __init__(self):
        super().__init__()
        self.__immortals = Immortals()

    def save_meta(self, meta: Meta, identifier: ID) -> bool:
        pass

    def save_profile(self, profile: Profile, identifier: ID = None) -> bool:
        pass

    def save_members(self, members: list, identifier: ID) -> bool:
        pass

    #
    #   EntityDataSource
    #
    def meta(self, identifier: ID) -> Optional[Meta]:
        return self.__immortals.meta(identifier=identifier)

    def profile(self, identifier: ID) -> Optional[Profile]:
        return self.__immortals.profile(identifier=identifier)

    #
    #   UserDataSource
    #
    def contacts(self, identifier: ID) -> Optional[list]:
        pass

    def private_key_for_signature(self, identifier: ID) -> Optional[SignKey]:
        return self.__immortals.private_key_for_signature(identifier=identifier)

    def private_keys_for_decryption(self, identifier: ID) -> Optional[list]:
        return self.__immortals.private_keys_for_decryption(identifier=identifier)
