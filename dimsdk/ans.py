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
    Address Name Service
    ~~~~~~~~~~~~~~~~~~~~

    A map for short name to ID, just like DNS
"""

from typing import Optional

from mkm.address import ANYWHERE

from dimp import ID, ANYONE, EVERYONE


class AddressNameService:

    def __init__(self):
        super().__init__()
        # Constant ID
        moky = ID.new(name='moky', address=ANYWHERE)
        # Reserved names
        keywords = ['all', 'everyone', 'anyone', 'owner', 'founder',
                    'root', 'admin', 'administrator', 'assistant',
                    'dkd', 'mkm', 'dimp', 'dim', 'dimt',
                    ]
        self.__reversed = keywords
        # ANS records
        self.__caches = {
            'all': EVERYONE,
            'everyone': EVERYONE,
            'anyone': ANYONE,
            'owner': ANYONE,
            'founder': moky,
        }

    def save_record(self, name: str, identifier: ID=None) -> bool:
        """ Save ANS record """
        if name in self.__reversed:
            # this name is reserved, cannot register
            return False
        if identifier is None:
            self.__caches.pop(name, None)
        else:
            self.__caches[name] = identifier
        # TODO: save this record into database
        return True

    def record(self, name: str) -> Optional[ID]:
        """ Get ID by short name """
        return self.__caches.get(name)

    def names(self, identifier: ID) -> Optional[list]:
        """ Get all short names with this ID """
        array = []
        for (key, value) in self.__caches.items():
            if key == identifier:
                array.append(value)
        return array
