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
    Station & Service Provider (SP)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Station : DIM network server node
    SP      : DIM network service provider
"""

from typing import Optional, List

from mkm.types import Converter

from dimp import EntityType, ID, Meta, Document, Visa
from dimp import ANYWHERE, EVERYWHERE
from dimp import User, UserDataSource
from dimp.mkm import Identifier, BaseUser, BaseGroup


class Station(User):

    ANY = Identifier(identifier='station@anywhere', name='station', address=ANYWHERE)
    EVERY = Identifier(identifier='stations@everywhere', name='stations', address=EVERYWHERE)

    def __init__(self, identifier: ID = None, host: str = None, port: int = 0):
        super().__init__()
        if identifier is None:
            identifier = self.ANY
        else:
            assert identifier.type == EntityType.STATION, 'Station ID type error: %s' % identifier
        self.__user = BaseUser(identifier=identifier)
        self.__host = host
        self.__port = port
        self.__isp: Optional[ID] = None

    # Override
    def __str__(self) -> str:
        """ Return str(self). """
        clazz = self.__class__.__name__
        identifier = self.identifier
        network = identifier.address.type
        return '<%s id="%s" network=%d host="%s" port=%d />' % (clazz, identifier, network, self.host, self.port)

    # Override
    def __eq__(self, other) -> bool:
        """ Return self==value. """
        if isinstance(other, Station):
            # check ID, host & port
            return same_stations(self, other)
        # check with inner user's ID
        return self.__user == other

    # Override
    def __ne__(self, other) -> bool:
        """ Return self!=value. """
        if isinstance(other, Station):
            # check ID, host & port
            return not same_stations(self, other)
        # check with inner user's ID
        return self.__user != other

    def reload(self):
        """ Reload station info: host & port, SP ID """
        doc = self.document()
        if doc is not None:
            host = doc.get_property(key='host')
            if host is not None:
                self.__host = Converter.get_str(value=host, default=None)
            port = doc.get_property(key='port')
            if port is not None:
                self.__port = Converter.get_int(value=port, default=0)
            isp = doc.get_property(key='ISP')
            if isp is not None:
                self.__isp = ID.parse(identifier=isp)

    #
    #   Server
    #

    @property
    def host(self) -> str:
        if self.__host is None:
            self.reload()
        return self.__host

    @property
    def port(self) -> int:
        if self.__port == 0:
            self.reload()
        return self.__port

    @property
    def provider(self) -> Optional[ID]:
        if self.__isp is None:
            self.reload()
        return self.__isp

    #
    #   Entity
    #

    @property  # Override
    def identifier(self) -> ID:
        return self.__user.identifier

    @identifier.setter
    def identifier(self, sid: ID):
        user = BaseUser(identifier=sid)
        user.data_source = self.data_source
        self.__user = user

    @property  # Override
    def type(self) -> int:
        return self.__user.type

    @property  # Override
    def data_source(self) -> Optional[UserDataSource]:
        return self.__user.data_source

    @data_source.setter  # Override
    def data_source(self, delegate: UserDataSource):
        self.__user.data_source = delegate

    @property  # Override
    def meta(self) -> Meta:
        return self.__user.meta

    # Override
    def document(self, doc_type: str = '*') -> Optional[Document]:
        return self.__user.document(doc_type=doc_type)

    #
    #   User
    #

    @property  # Override
    def visa(self) -> Optional[Visa]:
        return self.__user.visa

    @property  # Override
    def contacts(self) -> List[ID]:
        return self.__user.contacts

    # Override
    def verify(self, data: bytes, signature: bytes) -> bool:
        return self.__user.verify(data=data, signature=signature)

    # Override
    def encrypt(self, data: bytes) -> bytes:
        return self.__user.encrypt(data=data)

    # Override
    def sign(self, data: bytes) -> bytes:
        return self.__user.sign(data=data)

    # Override
    def decrypt(self, data: bytes) -> Optional[bytes]:
        return self.__user.decrypt(data=data)

    # Override
    def sign_visa(self, visa: Visa) -> Visa:
        return self.__user.sign_visa(visa=visa)

    # Override
    def verify_visa(self, visa: Visa) -> bool:
        return self.__user.verify_visa(visa=visa)


class ServiceProvider(BaseGroup):

    def __init__(self, identifier: ID):
        super().__init__(identifier=identifier)
        assert identifier.type == EntityType.ISP, 'Service Provider ID type error: %s' % identifier

    @property
    def stations(self) -> List:
        doc = self.document()
        if doc is not None:
            array = doc.get_property(key='stations')
            if array is not None:
                return array
        # TODO: load from local storage
        return []

#
#   Comparison
#


def same_stations(a: Station, b: Station) -> bool:
    if a is b:
        # same object
        return True
    else:
        return check_identifiers(a.identifier, b.identifier) and \
               check_hosts(a.host, b.host) and \
               check_ports(a.port, b.port)


def check_identifiers(a: ID, b: ID) -> bool:
    if a is b:
        # same object
        return True
    elif a.is_broadcast or b.is_broadcast:
        return True
    else:
        return a == b


def check_hosts(a: Optional[str], b: Optional[str]) -> bool:
    if a is None or b is None:
        return True
    elif len(a) == 0 or len(b) == 0:
        return True
    else:
        return a == b


def check_ports(a: Optional[int], b: Optional[int]) -> bool:
    if a is None or b is None:
        return True
    elif a == 0 or b == 0:
        return True
    else:
        return a == b
