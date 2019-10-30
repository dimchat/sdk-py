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
    Immortals
    ~~~~~~~~~

    Immortal accounts (for test)
"""

import os
from typing import Optional

from dimp import ID, Profile, Meta
from dimp import UserDataSource
from mkm import PrivateKey, PublicKey

from .dos import JSONFile


def load_resource_file(filename: str) -> dict:
    directory = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(directory, 'res', filename)
    file = JSONFile(path=path)
    return file.read()


def sign_profile(profile: Profile, private_key: PrivateKey) -> Profile:
    # set 'name'
    names = profile.get('names')
    if names is None:
        name = profile.get('name')
        if name is not None:
            profile.set_property('name', name)
    elif len(names) > 0:
        name = names[0]
        profile.set_property('name', name)
    # set 'avatar'
    avatar = profile.get('avatar')
    if avatar is not None:
        profile.set_property('avatar', avatar)
    profile.sign(private_key=private_key)
    return profile


def verify_profile(profile: Profile, public_key: PublicKey) -> Optional[Profile]:
    if profile.verify(public_key=public_key):
        return profile


class Immortals(UserDataSource):

    def __init__(self):
        super().__init__()
        # caches
        self.__ids = {}
        self.__metas = {}
        self.__private_keys = {}
        self.__profiles = {}
        # load built-in accounts
        self.__load(filename='mkm_hulk.js')
        self.__load(filename='mkm_moki.js')

    def __load(self, filename: str):
        config = load_resource_file(filename=filename)
        if config is None:
            # file not found
            return False
        # ID
        identifier = ID(config.get('ID'))
        assert identifier.valid, 'ID not valid: %s' % identifier
        self.__ids[identifier] = identifier
        # meta
        meta = Meta(config.get('meta'))
        assert meta.match_identifier(identifier), 'meta not match ID: %s, %s' % (identifier, meta)
        self.__metas[identifier] = meta
        # private key
        private_key = PrivateKey(config.get('privateKey'))
        if private_key is not None:
            self.__private_keys[identifier] = private_key
        # profile
        profile = Profile(config.get('profile'))
        if profile is not None:
            # try to verify it
            tai = verify_profile(profile=profile, public_key=meta.key)
            if tai is None and private_key is not None:
                tai = sign_profile(profile=profile, private_key=private_key)
            if tai is not None:
                profile = tai
            self.__profiles[identifier] = profile

    #
    #   EntityDataSource
    #
    def meta(self, identifier: ID) -> Optional[Meta]:
        return self.__metas.get(identifier)

    def profile(self, identifier: ID) -> Optional[Profile]:
        return self.__profiles.get(identifier)

    #
    #   UserDataSource
    #
    def private_key_for_signature(self, identifier: ID) -> Optional[PrivateKey]:
        return self.__private_keys.get(identifier)

    def private_keys_for_decryption(self, identifier: ID) -> Optional[list]:
        key = self.__private_keys.get(identifier)
        if key is not None:
            return [key]

    def contacts(self, identifier: ID) -> Optional[list]:
        pass
