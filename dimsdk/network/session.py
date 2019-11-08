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
    Session Server
    ~~~~~~~~~~~~~~

    for login user
"""

import numpy

from dimp import ID

from ..crypto import hex_encode


class Session:

    def __init__(self, identifier: ID, client_address):
        super().__init__()
        # user ID
        self.__identifier = identifier
        # (IP, port)
        self.__client_address = client_address
        # generate session key
        self.__session_key = hex_encode(bytes(numpy.random.bytes(32)))
        # valid flag: when handshake accepted, this should be set to True
        self.valid = False
        # active status: when the client entered background, it should be set to False
        self.active = True

    def __str__(self):
        clazz = self.__class__.__name__
        return '<%s:%s %s|%s valid=%d active=%d />' % (clazz,
                                                       self.__session_key,
                                                       self.__client_address,
                                                       self.__identifier,
                                                       self.valid,
                                                       self.active)

    @property
    def identifier(self) -> ID:
        return self.__identifier

    @property
    def client_address(self):  # (IP, port)
        return self.__client_address

    @property
    def session_key(self) -> str:
        return self.__session_key


class SessionServer:

    def __init__(self):
        super().__init__()
        # memory cache
        self.__pool = {}  # {identifier: [session]}

    def all(self, identifier: ID) -> list:
        """ Get all sessions of this user """
        return self.__pool.get(identifier)

    def clear(self, identifier: ID) -> bool:
        """ Remove all sessions of this user """
        if identifier in self.__pool:
            self.__pool.pop(identifier)
            return True

    def add(self, session: Session) -> bool:
        """ Add a session with ID into memory cache """
        identifier = session.identifier
        # 1. get all sessions with identifier
        array: list = self.all(identifier)
        if array is None:
            # 2.1. set a list contains this session object
            self.__pool[identifier] = [session]
            return True
        else:
            # 2.2. check each session with client address
            client_address = session.client_address
            for item in array:
                assert isinstance(item, Session), 'session error: %s' % item
                if item.client_address == client_address:
                    # already exists
                    return False
            # 3. add this session object to the current array
            array.append(session)
            return True

    def remove(self, session: Session) -> bool:
        """ Remove the session from memory cache """
        identifier = session.identifier
        # 1. get all sessions with identifier
        array: list = self.all(identifier)
        if array is not None:
            count = len(array)
            if count == 0:
                # 2.1. empty array, remove it
                self.clear(identifier)
            elif count == 1:
                # 2.2. check the only one session
                if array[0].client_address == session.client_address:
                    # exactly
                    self.clear(identifier)
                    return True
            else:
                # 2.3. check each session with client address
                for item in array:
                    assert isinstance(item, Session), 'session error: %s' % item
                    if item.client_address == session.client_address:
                        # got it
                        array.remove(session)
                        return True

    def get(self, identifier: ID, client_address) -> Session:
        """ Search session with ID and client address """
        array: list = self.all(identifier)
        if array is not None:
            for item in array:
                assert isinstance(item, Session), 'session error: %s' % item
                if item.client_address == client_address:
                    # got it
                    return item

    def new(self, identifier: ID, client_address):
        """ Session factory """
        session = self.get(identifier=identifier, client_address=client_address)
        if session is None:
            # create a new session
            session = Session(identifier=identifier, client_address=client_address)
            self.add(session=session)
        return session

    #
    #   Users
    #
    def all_users(self) -> list:
        """ Get all users """
        return list(self.__pool.keys())

    def online_users(self) -> list:
        """ Get online users """
        keys = self.all_users()
        array = []
        for identifier in keys:
            sessions = self.all(identifier)
            if sessions is None:
                # should not happen
                continue
            for item in sessions:
                assert isinstance(item, Session), 'session error: %s' % item
                if item.valid and item.active:
                    # got it
                    array.append(identifier)
                    break
        return array
