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
    Facebook
    ~~~~~~~~

    Barrack for cache entities
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from dimp import EntityType, ID
from dimp import User, Group
from dimp import Meta, Document
from dimp import DocumentHelper
from dimp import Barrack
from dimp import BaseUser, BaseGroup

from .mkm import ServiceProvider, Station, Bot

from .archivist import Archivist


class Facebook(Barrack, ABC):

    @property
    @abstractmethod
    def archivist(self) -> Archivist:
        raise NotImplemented

    # Override
    def create_user(self, identifier: ID) -> Optional[User]:
        assert identifier.is_user, 'user ID error: %s' % identifier
        # check visa key
        if not identifier.is_broadcast:
            if self.public_key_for_encryption(identifier=identifier) is None:
                # assert False, 'visa.key not found: %s' % identifier
                return None
            #
            #   NOTICE: if visa.key exists, then visa & meta must exist too.
            #
        network = identifier.type
        # check user type
        if network == EntityType.STATION:
            return Station(identifier=identifier)
        elif network == EntityType.BOT:
            return Bot(identifier=identifier)
        # general user, or 'anyone@anywhere'
        return BaseUser(identifier=identifier)

    # Override
    def create_group(self, identifier: ID) -> Optional[Group]:
        assert identifier.is_group, 'group ID error: %s' % identifier
        # check members
        if not identifier.is_broadcast:
            members = self.members(identifier=identifier)
            if len(members) == 0:
                # assert False, 'group members not found: %s' % identifier
                return None
            #
            #   NOTICE: if members exist, then owner (founder) must exist,
            #           and bulletin & meta must exist too.
            #
        network = identifier.type
        # check group type
        if network == EntityType.ISP:
            return ServiceProvider(identifier=identifier)
        # general group, or 'everyone@everywhere'
        return BaseGroup(identifier=identifier)

    @property
    @abstractmethod
    def local_users(self) -> List[User]:
        """
        Get all local users (for decrypting received message)

        :return: users with private key
        """
        raise NotImplemented

    def select_user(self, receiver: ID) -> Optional[User]:
        """ Select local user for receiver """
        users = self.local_users
        if len(users) == 0:
            assert False, 'local users should not be empty'
            # return None
        elif receiver.is_broadcast:
            # broadcast message can decrypt by anyone, so just return current user
            return users[0]
        elif receiver.is_user:
            # 1. personal message
            # 2. split group message
            for item in users:
                if item.identifier == receiver:
                    # DISCUSS: set this item to be current user?
                    return item
            # not me?
            return None
        # group message (recipient not designated)
        assert receiver.is_group, 'receiver error: %s' % receiver
        # the messenger will check group info before decrypting message,
        # so we can trust that the group's meta & members MUST exist here.
        members = self.members(identifier=receiver)
        assert len(members) > 0, 'members not found: %s' % receiver
        for item in users:
            if item.identifier in members:
                # DISCUSS: set this item to be current user?
                return item

    def save_meta(self, meta: Meta, identifier: ID) -> bool:
        if meta.valid and meta.match_identifier(identifier=identifier):
            # meta ok
            pass
        else:
            # assert False, 'meta not valid: %s' % identifier
            return False
        # check old meta
        old = self.meta(identifier=identifier)
        if old is not None:
            # assert meta == old, 'meta should not changed'
            return True
        # meta not exists yet, save it
        db = self.archivist
        return db.save_meta(meta=meta, identifier=identifier)

    def save_document(self, document: Document) -> bool:
        identifier = document.identifier
        # assert identifier is not None, 'document error: %s' % document
        if not document.valid:
            # try to verify
            meta = self.meta(identifier=identifier)
            if meta is None:
                # assert False, 'meta not found: %s' % identifier
                return False
            elif document.verify(public_key=meta.public_key):
                # document ok
                pass
            else:
                # assert False, 'failed to verify document: %s' % identifier
                return False
        doc_type = document.type
        if doc_type is None:
            doc_type = '*'
        # check old documents with type
        all_documents = self.documents(identifier=identifier)
        old_doc = DocumentHelper.last_document(documents=all_documents, doc_type=doc_type)
        if old_doc is not None and DocumentHelper.is_expired(document, old_doc):
            # assert False, 'drop expired document: %s' % identifier
            return False
        # document ok, save it
        db = self.archivist
        return db.save_document(document=document)

    #
    #   EntityDataSource
    #

    # Override
    def meta(self, identifier: ID) -> Optional[Meta]:
        # if identifier.is_broadcast:
        #     # broadcast ID has no meta
        #     return None
        db = self.archivist
        info = db.meta(identifier=identifier)
        db.check_meta(identifier=identifier, meta=info)
        return info

    # Override
    def documents(self, identifier: ID) -> List[Document]:
        if identifier.is_broadcast:
            # broadcast ID has no documents
            return []
        db = self.archivist
        docs = db.documents(identifier=identifier)
        db.check_documents(identifier=identifier, documents=docs)
        return docs
