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

from dimp import PublicKey
from dimp import ID, NetworkID, User, Group

from .certificate import CertificateAuthority


class Station(User):

    def __init__(self, identifier: ID, host: str=None, port: int=0):
        super().__init__(identifier=identifier)
        assert identifier.type == NetworkID.Station, 'Station ID type error: %s' % identifier
        self.__host = host
        self.__port = port

    def __str__(self):
        clazz = self.__class__.__name__
        identifier = self.identifier
        network = identifier.address.network
        number = identifier.address.number
        name = self.name
        host = self.host
        port = self.port
        return '<%s: %s(%s|%d) "%s" host="%s" port=%d />' % (clazz, identifier, network, number, name, host, port)

    @property
    def host(self) -> str:
        if self.__host is None:
            profile = self.profile
            if profile is not None:
                value = profile.get_property('host')
                if value is not None:
                    self.__host = str(value)
            if self.__host is None:
                self.__host = '0.0.0.0'
        return self.__host

    @property
    def port(self) -> int:
        if self.__port is 0:
            profile = self.profile
            if profile is not None:
                value = profile.get_property('port')
                if value is not None:
                    self.__port = int(value)
            if self.__port is 0:
                self.__port = 9394
        return self.__port

    @classmethod
    def new(cls, station: dict):
        # ID
        identifier = ID(station['ID'])
        # host
        host = station['host']
        # port
        port = station.get('port')
        if port is None:
            port = 9394
        else:
            port = int(port)
        # Certificate Authority
        if 'CA' in station['CA']:
            certificate = CertificateAuthority(station['CA'])
        else:
            certificate = None
        # Service Provider's ID
        if 'SP' in station['SP']:
            provider = station['SP']
            if isinstance(provider, dict):
                provider = ID(provider['ID'])
            elif isinstance(provider, str):
                provider = ID(provider)
            else:
                raise TypeError('Service Provider data format error')
        else:
            provider = None

        # create Station object
        if identifier.type == NetworkID.Station:
            self = Station(identifier=identifier, host=host, port=port)
            self.provider = provider
            self.certificate = certificate
            return self
        else:
            raise ValueError('Station ID error')


class ServiceProvider(Group):

    def __init__(self, identifier: ID):
        super().__init__(identifier=identifier)
        assert identifier.type == NetworkID.Provider, 'Service Provider ID type error: %s' % identifier

    @property
    def stations(self):
        return self.members

    @classmethod
    def new(cls, provider: dict):
        # ID
        identifier = ID(provider['ID'])
        # Public Key
        if 'publicKey' in provider:
            public_key = PublicKey(provider['publicKey'])
        elif 'PK' in provider:
            public_key = PublicKey(provider['PK'])
        else:
            public_key = None
        # Certificate Authority
        if 'CA' in provider['CA']:
            certificate = CertificateAuthority(provider['CA'])
            if public_key is None:
                # get public key from the CA info
                public_key = certificate.info.key
        else:
            certificate = None

        # create ServiceProvider object
        if identifier.type == NetworkID.Provider:
            self = ServiceProvider(identifier=identifier)
            self.publicKey = public_key
            self.certificate = certificate
            return self
        else:
            raise ValueError('Service provider ID error')
