# -*- coding: utf-8 -*-
from typing import Optional

from mkm import ID, PrivateKey, Profile, Meta
from mkm.immortals import Immortals

from dimsdk import Facebook


class Database(Facebook):

    def __init__(self):
        super().__init__()
        self.__immortals = Immortals()

    def save_meta(self, meta: Meta, identifier: ID) -> bool:
        pass

    def load_meta(self, identifier: ID) -> Optional[Meta]:
        pass

    def save_profile(self, profile: Profile, identifier: ID = None) -> bool:
        pass

    def load_profile(self, identifier: ID) -> Optional[Profile]:
        pass

    def save_private_key(self, key: PrivateKey, identifier: ID) -> bool:
        pass

    def load_private_key(self, identifier: ID) -> Optional[PrivateKey]:
        pass

    def save_contacts(self, contacts: list, identifier: ID) -> bool:
        pass

    def load_contacts(self, identifier: ID) -> Optional[list]:
        pass

    def save_members(self, members: list, identifier: ID) -> bool:
        pass

    def load_members(self, identifier: ID) -> Optional[list]:
        pass

    def save_assistants(self, assistants: list, identifier: ID) -> bool:
        pass

    def load_assistants(self, identifier: ID) -> Optional[list]:
        pass

    #
    #   EntityDataSource
    #
    def meta(self, identifier: ID) -> Optional[Meta]:
        info = super().meta(identifier=identifier)
        if info is not None:
            return info
        return self.__immortals.meta(identifier=identifier)
