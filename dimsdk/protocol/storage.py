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
    Storage Protocol
    ~~~~~~~~~~~~~~~~

    Storage data (may be encrypted) by title for VIP users
"""

import json
from typing import Optional

from dimp import Base64
from dimp import DecryptKey, SymmetricKey, ID
from dimp import Command


class StorageCommand(Command):
    """
        Storage Command
        ~~~~~~~~~~~~~~~

        data format: {
            type : 0x88,
            sn   : 123,

            command : "storage", // command name
            title   : "...",     // "contacts", "private_key", ...

            data    : "...",  // base64_encode(symmetric)
            key     : "...",  // base64_encode(asymmetric)
            //-- extra info
        }
    """

    STORAGE = 'storage'

    CONTACTS = 'contacts'
    PRIVATE_KEY = 'private_key'

    def __new__(cls, cmd: dict):
        """
        Create storage command

        :param cmd: command info
        :return: StorageCommand object
        """
        if cmd is None:
            return None
        elif cls is StorageCommand:
            if isinstance(cmd, StorageCommand):
                # return StorageCommand object directly
                return cmd
        # new StorageCommand(dict)
        return super().__new__(cls, cmd)

    def __init__(self, content: dict):
        if self is content:
            # no need to init again
            return
        super().__init__(content)
        # lazy
        self.__key: bytes = None
        self.__data: bytes = None
        self.__plaintext: object = None

    #
    #   Title
    #
    @property
    def title(self) -> str:
        string = self.get('title')
        if string is None or len(string) == 0:
            string = self.command
            assert string != self.STORAGE, 'storage command error: %s' % self
        return string

    #
    #   ID
    #
    @property
    def identifier(self) -> ID:
        return self.delegate.identifier(string=self.get('ID'))

    @identifier.setter
    def identifier(self, value: str):
        if value is None:
            self.pop('ID', None)
        else:
            self['ID'] = value

    #
    #   Key (for decrypt data)
    #
    @property
    def key(self) -> Optional[bytes]:
        if self.__key is None:
            base64 = self.get('key')
            if base64 is not None:
                self.__key = Base64.decode(base64)
        return self.__key

    @key.setter
    def key(self, value: bytes):
        if value is None:
            self.pop('key', None)
        else:
            self['key'] = Base64.encode(value)
        self.__key = value

    #
    #   Data (encrypted)
    #
    @property
    def data(self) -> Optional[bytes]:
        if self.__data is None:
            base64 = self.get('data')
            if base64 is not None:
                self.__data = Base64.decode(base64)
        return self.__data

    @data.setter
    def data(self, value: bytes):
        if value is None:
            self.pop('data', None)
        else:
            self['data'] = Base64.encode(value)
        self.__data = value

    def decrypt(self, password: DecryptKey=None, private_key: DecryptKey=None) -> bytes:
        """
        Decrypt data
            1. decrypt key with private key (such as RSA) to a password
            2. decrypt data with password (symmetric key, such as AES, DES, ...)

        :param password:    symmetric key
        :param private_key: asymmetric private key
        :return: plaintext
        """
        if self.__plaintext is None:
            # get symmetric key
            key = None
            if password is not None:
                assert isinstance(password, SymmetricKey), 'password error: %s' % password
                key = password
            elif private_key is not None:
                # assert isinstance(private_key, PrivateKey), 'private key error: %s' % private_key
                key_data = private_key.decrypt(self.key)
                key = SymmetricKey(json.loads(key_data))
            # get encrypted data
            data = self.data
            if key is not None and data is not None:
                self.__plaintext = key.decrypt(data=data)
        return self.__plaintext

#
    #   Factories
    #
    @classmethod
    def new(cls, content: dict=None, title: str=None, time: int=0):
        """
        Create storage command

        :param content: command info
        :param title: title
        :param time: command time
        :return: StorageCommand object
        """
        if content is None:
            # create empty content
            content = {}
        # new StorageCommand(dict)
        if title is not None:
            if title == cls.CONTACTS:
                # compatible with v1.0
                return super().new(content=content, command=cls.CONTACTS)
            content['title'] = title
        return super().new(content=content, command=cls.STORAGE, time=time)


# register command class
Command.register(command=StorageCommand.STORAGE, command_class=StorageCommand)
Command.register(command=StorageCommand.CONTACTS, command_class=StorageCommand)
Command.register(command=StorageCommand.PRIVATE_KEY, command_class=StorageCommand)
