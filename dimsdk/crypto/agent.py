# -*- coding: utf-8 -*-
#
#   DIM-SDK : Decentralized Instant Messaging Software Development Kit
#
#                                Written in 2026 by Moky <albert.moky@gmail.com>
#
# ==============================================================================
# MIT License
#
# Copyright (c) 2026 Albert Moky
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
from typing import Optional, Union, Set, List

from dimp import VerifyKey, EncryptKey
from dimp import PublicKey
from dimp import Meta, Document, Visa
from dimp import GeneralAccountHelper
from dimp import GeneralAccountExtension, shared_account_extensions

from .bundle import EncryptedBundle, UserEncryptedBundle


class VisaAgent(ABC):

    @abstractmethod
    def encrypt_bundle(self, plaintext: bytes, meta: Meta, documents: List[Document]) -> EncryptedBundle:
        raise NotImplemented

    @abstractmethod
    def get_verify_keys(self, meta: Meta, documents: List[Document]) -> List[VerifyKey]:
        raise NotImplemented

    @abstractmethod
    def get_terminals(self, documents: List[Document]) -> Set[str]:
        raise NotImplemented


# noinspection PyMethodMayBeStatic
class DefaultVisaAgent(VisaAgent):

    # Override
    def encrypt_bundle(self, plaintext: bytes, meta: Meta, documents: List[Document]) -> EncryptedBundle:
        # NOTICE: meta.key will never changed, so use visa.key to encrypt message
        #         is a better way
        bundle = UserEncryptedBundle()
        #
        #  1. encrypt with visa keys
        #
        for doc in documents:
            # encrypt by public key
            pub_key = self.get_encrypt_key(document=doc)
            if pub_key is None:
                continue
            # get visa.terminal
            terminal = self.get_terminal(document=doc)
            if terminal is None or len(terminal) == 0:
                terminal = '*'
            if bundle.get(terminal) is not None:
                # assert False, 'duplicated visa key: %s' % doc
                continue
            ciphertext = pub_key.encrypt(plaintext=plaintext)
            bundle[terminal] = ciphertext
        if bundle.is_empty:
            #
            #  2. encrypt with meta key
            #
            meta_key = meta.public_key
            if isinstance(meta_key, EncryptKey):
                # terminal = '*
                ciphertext = meta_key.encrypt(plaintext=plaintext)
                bundle['*'] = ciphertext
        # OK
        return bundle

    # Override
    def get_verify_keys(self, meta: Meta, documents: List[Document]) -> List[VerifyKey]:
        verify_keys = []
        # the sender may use communication key to sign message.data,
        # try to verify it with visa.key first;
        for doc in documents:
            pub_key = self.get_verify_key(document=doc)
            if pub_key is not None:
                verify_keys.append(pub_key)
            # else:
            #     assert False, 'failed to get visa key: %s' % doc
        # the sender may use identity key to sign message.data,
        # try to verify it with meta.key too.
        verify_keys.append(meta.public_key)
        # OK
        return verify_keys

    # protected
    def get_verify_key(self, document: Document) -> Optional[VerifyKey]:
        if isinstance(document, Visa):
            visa_key = document.public_key
            if isinstance(visa_key, VerifyKey):
                return visa_key
            # assert False, 'visa key error: %s, %s' % (visa_key, document)
            return None
        # public key in user profile?
        key = document.get_property(name='key')
        return PublicKey.parse(key=key)

    # protected
    def get_encrypt_key(self, document: Document) -> Optional[EncryptKey]:
        if isinstance(document, Visa):
            visa_key = document.public_key
            if visa_key is not None:
                return visa_key
            # assert False, 'failed to get visa key: %s' % document
            return None
        key = document.get_property(name='key')
        pub_key = PublicKey.parse(key=key)
        if pub_key is None:
            # profile document?
            return None
        elif isinstance(pub_key, EncryptKey):
            return pub_key
        # else:
        #     assert False, 'visa key error: %s' % pub_key

    # protected
    def get_terminal(self, document: Document) -> Optional[str]:
        terminal = document.get_str(key='terminal')
        if terminal is None:
            # get from document ID
            helper = account_helper()
            info = document.to_dict()
            did = helper.get_document_id(document=info)
            if did is not None:
                return did.terminal
            # else:
            #     assert False, 'document ID not found: %s' % document
            #     # TODO: get from property?
        return terminal

    # Override
    def get_terminals(self, documents: List[Document]) -> Set[str]:
        devices = set()
        for doc in documents:
            terminal = self.get_terminal(document=doc)
            if terminal is None or len(terminal) == 0:
                terminal = '*'
            devices.add(terminal)
        # OK
        return devices


# -----------------------------------------------------------------------------
#  Account Extensions
# -----------------------------------------------------------------------------


class VisaAgentExtension:

    @property
    def visa_agent(self) -> VisaAgent:
        raise NotImplemented

    @visa_agent.setter
    def visa_agent(self, agent: VisaAgent):
        raise NotImplemented


shared_account_extensions.visa_agent: VisaAgent = DefaultVisaAgent()


def account_extensions() -> Union[VisaAgentExtension, GeneralAccountExtension]:
    return shared_account_extensions


def visa_agent() -> VisaAgent:
    ext = account_extensions()
    return ext.visa_agent


def account_helper() -> GeneralAccountHelper:
    ext = account_extensions()
    return ext.helper
