# -*- coding: utf-8 -*-
#
#   DIM-SDK : Decentralized Instant Messaging Software Development Kit
#
#                                Written in 2023 by Moky <albert.moky@gmail.com>
#
# ==============================================================================
# MIT License
#
# Copyright (c) 2023 Albert Moky
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

from abc import ABC, abstractmethod
from typing import Optional, List

from dimp import DateTime
from dimp import ID, Meta, Document
from dimp import EntityDataSource

from .utils import FrequencyChecker
from .utils import RecentTimeChecker


class Archivist(EntityDataSource, ABC):

    # each query will be expired after 10 minutes
    QUERY_EXPIRES = 600.0  # seconds

    def __init__(self, expires: float):
        super().__init__()
        # query checkers
        self.__meta_queries = FrequencyChecker(expires=expires)
        self.__docs_queries = FrequencyChecker(expires=expires)
        self.__members_queries = FrequencyChecker(expires=expires)
        # recent time checkers
        self.__last_document_times = RecentTimeChecker()
        self.__last_history_times = RecentTimeChecker()

    # protected
    def is_meta_query_expired(self, identifier: ID) -> bool:
        return self.__meta_queries.is_expired(key=identifier)

    # protected
    def is_documents_query_expired(self, identifier: ID) -> bool:
        return self.__docs_queries.is_expired(key=identifier)

    # protected
    def is_members_query_expired(self, group: ID) -> bool:
        return self.__members_queries.is_expired(key=group)

    #
    #   Meta
    #

    # protected
    # noinspection PyMethodMayBeStatic
    def needs_query_meta(self, identifier: ID, meta: Optional[Meta]) -> bool:
        """ check whether need to query meta """
        if identifier.is_broadcast:
            # broadcast entity has no meta to query
            return False
        elif meta is None:
            # meta not found, sure to query
            return True
        # assert meta.match_identifier(identifier), 'meta not match: %s, %s' % (identifier, meta)

    #
    #   Last Document Times
    #

    def set_last_document_time(self, identifier: ID, last_time: Optional[DateTime]):
        return self.__last_document_times.set_last_time(key=identifier, last_time=last_time)

    # protected
    def needs_query_documents(self, identifier: ID, documents: List[Document]) -> bool:
        """ check whether need to query documents """
        if identifier.is_broadcast:
            # broadcast entity has no document to query
            return False
        # elif documents is None:
        #     # assert False, 'should not happen'
        #     return True
        elif len(documents) == 0:
            # documents not found, sure to query
            return True
        current = self.get_last_document_time(identifier=identifier, documents=documents)
        return self.__last_document_times.is_expired(key=identifier, now=current)

    # protected
    # noinspection PyMethodMayBeStatic
    def get_last_document_time(self, identifier: ID, documents: List[Document]) -> Optional[DateTime]:
        if documents is None or len(documents) == 0:
            return None
        last_time: Optional[DateTime] = None
        for doc in documents:
            assert doc.identifier == identifier, 'document not match: %s, %s' % (identifier, doc)
            doc_time = doc.time
            if doc_time is None:
                # assert False, 'document error: %s' % doc
                pass
            elif last_time is None or last_time.before(doc_time):
                last_time = doc_time
        # got
        return last_time

    #
    #   Last Group History Times
    #

    def set_last_group_history_time(self, group: ID, last_time: Optional[DateTime]):
        return self.__last_history_times.set_last_time(key=group, last_time=last_time)

    # protected
    def needs_query_members(self, group: ID, members: List[ID]) -> bool:
        """ check whether need to query group members """
        if group.is_broadcast:
            # broadcast group has no members to query
            return False
        # elif members is None:
        #     # assert False, 'should not happen'
        #     return True
        elif len(members) == 0:
            # members not found, sure to query
            return True
        current = self.get_last_group_history_time(group=group)
        return self.__last_history_times.is_expired(key=group, now=current)

    # protected
    @abstractmethod
    def get_last_group_history_time(self, group: ID) -> Optional[DateTime]:
        raise NotImplemented

    #
    #   Checking
    #

    def check_meta(self, identifier: ID, meta: Optional[Meta]) -> bool:
        """
        Check meta for querying

        :param identifier: entity ID
        :param meta:       exists meta
        :return: true on querying
        """
        if self.needs_query_meta(identifier=identifier, meta=meta):
            # if not self.is_meta_query_expired(identifier=identifier):
            #     # query not expired yet
            #     return False
            return self.query_meta(identifier=identifier)
        # no need to query meta again
        return False

    def check_documents(self, identifier: ID, documents: List[Document]) -> bool:
        """
        Check documents for querying/updating

        :param identifier: entity ID
        :param documents:  exist documents
        :return: true on querying
        """
        if self.needs_query_documents(identifier=identifier, documents=documents):
            # if not self.is_documents_query_expired(identifier=identifier):
            #     # query not expired yet
            #     return False
            return self.query_documents(identifier=identifier, documents=documents)
        # no need to update document now
        return False

    def check_members(self, group: ID, members: List[ID]) -> bool:
        """
        Check group members for querying

        :param group:   group ID
        :param members: exist members
        :return: true on querying
        """
        if self.needs_query_members(group=group, members=members):
            # if not self.is_members_query_expired(group=group):
            #     # query not expired yet
            #     return False
            return self.query_members(group=group, members=members)
        # no need to update group members now
        return False

    #
    #   Querying
    #

    @abstractmethod
    def query_meta(self, identifier: ID) -> bool:
        """
        Request for meta with entity ID
        (call 'isMetaQueryExpired()' before sending command)

        :param identifier: entity ID
        :return: false on duplicated
        """
        raise NotImplemented

    @abstractmethod
    def query_documents(self, identifier: ID, documents: List[Document]) -> bool:
        """
        Request for documents with entity ID
        (call 'isDocumentQueryExpired()' before sending command)

        :param identifier: entity ID
        :param documents:  exist documents
        :return: false on duplicated
        """
        raise NotImplemented

    @abstractmethod
    def query_members(self, group: ID, members: List[ID]) -> bool:
        """
        Request for group members with group ID
        (call 'isMembersQueryExpired()' before sending command)

        :param group:   group ID
        :param members: exist members
        :return: false on duplicated
        """
        raise NotImplemented

    #
    #   Storage
    #

    @abstractmethod
    def save_meta(self, meta: Meta, identifier: ID) -> bool:
        """
        Save meta for entity ID (must verify first)

        :param meta:       entity meta
        :param identifier: entity ID
        :return: true on success
        """
        raise NotImplemented

    @abstractmethod
    def save_document(self, document: Document) -> bool:
        """
        Save entity document with ID (must verify first)

        :param document: entity document
        :return: true on success
        """
        raise NotImplemented
