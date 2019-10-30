# -*- coding: utf-8 -*-
#
#   DIM-SDK : Decentralized Instant Messaging Software Development Kit
#
#                                Written in 2019 by Moky <albert.moky@gmail.com>
#
# ==============================================================================
# MIT License
#
# Copyright (c) 2019 Albert Moky
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==============================================================================

"""
    Key Store
    ~~~~~~~~~

    Memory cache for reused passwords (symmetric key)
"""

import os
from typing import Optional

from mkm.dos import JSONFile

from dimp import ID, SymmetricKey, LocalUser
from dimp import KeyCache


class KeyStore(KeyCache):

    def __init__(self):
        super().__init__()
        self.__user: LocalUser = None
        self.__base_dir: str = '/tmp/.dim/'

    @property
    def user(self) -> Optional[LocalUser]:
        return self.__user

    @user.setter
    def user(self, value: LocalUser):
        if value is None:
            # save key map for old user
            self.flush()
            self.__user = None
        elif value != self.__user:
            # load key map for new user
            self.__user = value
            dictionary = self.load_keys()
            if dictionary is not None:
                self.update_keys(dictionary)

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
        return os.path.join(self.__base_dir, 'protected', self.__user.identifier, 'keystore.js')

    def save_keys(self, key_map: dict) -> bool:
        # write key table to persistent storage
        path = self.__path()
        if path is None:
            return False
        return JSONFile(path).write(key_map)

    def load_keys(self) -> Optional[dict]:
        # load key table from persistent storage
        path = self.__path()
        if path is None:
            return None
        return JSONFile(path).read()

    #
    #   ICipherKeyDataSource
    #
    def cipher_key(self, sender: ID, receiver: ID) -> Optional[SymmetricKey]:
        key = super().cipher_key(sender=sender, receiver=receiver)
        if key is None:
            if self.__user is not None and self.__user.identifier == sender:
                # create a new key & save it into the Key Store
                key = SymmetricKey({'algorithm': 'AES'})
                self.cache_cipher_key(key=key, sender=sender, receiver=receiver)
        return key

    def reuse_cipher_key(self, key: SymmetricKey, sender: ID, receiver: ID) -> Optional[SymmetricKey]:
        # TODO: check reuse key
        pass
