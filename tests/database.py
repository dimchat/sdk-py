# -*- coding: utf-8 -*-
from typing import Optional

from mkm import ID, PrivateKey, Profile, Meta

from dimsdk import Facebook


class Database(Facebook):

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
