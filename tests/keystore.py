# -*- coding: utf-8 -*-

"""
    Key Store
    ~~~~~~~~~

    Memory cache for reused passwords (symmetric key)
"""

import os
from typing import Optional

from dimsdk import User

from keycache import KeyCache


class KeyStore(KeyCache):

    def __init__(self):
        super().__init__()
        self.__user: Optional[User] = None
        self.__base_dir: str = '/tmp/.dim/'

    @property
    def user(self) -> Optional[User]:
        return self.__user

    @user.setter
    def user(self, value: User):
        if self.__user is not None:
            # save key map for old user
            self.flush()
            if self.__user == value:
                # user not changed
                return
        if value is None:
            self.__user = None
            return
        # change current user
        self.__user = value
        keys = self.load_keys()
        if keys is None:
            # failed to load cached keys for new user
            return
        # update key map
        self.update_keys(key_map=keys)

    @property
    def directory(self) -> str:
        return self.__base_dir

    @directory.setter
    def directory(self, value: str):
        self.__base_dir = value

    # '/tmp/.dim/protected/{ADDRESS}/keystore.js'
    def __path(self) -> Optional[str]:
        if self.__user is None:
            return None
        address = self.__user.identifier.address
        return os.path.join(self.__base_dir, 'protected', str(address), 'keystore.js')

    def save_keys(self, key_map: dict) -> bool:
        # write key table to persistent storage
        path = self.__path()
        if path is None:
            return False
        # return JSONFile(path).write(key_map)

    def load_keys(self) -> Optional[dict]:
        # load key table from persistent storage
        path = self.__path()
        if path is None:
            return None
        # return JSONFile(path).read()
