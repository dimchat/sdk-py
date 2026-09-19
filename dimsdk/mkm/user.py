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
    User Entity (with Visa-based Crypto)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from abc import ABC, abstractmethod
from typing import Optional, Set, List

from dimp import DecryptKey, SignKey
from dimp import ID, Document
from dimp import EncryptedBundle

from ..crypto.agent import visa_agent, account_handler

from .entity import EntityDataSource, Entity, BaseEntity


class UserDataSource(EntityDataSource, ABC):
    """Data source interface for user-specific data and cryptographic keys.

    Extends :class:`EntityDataSource` with user-specific key management, defining the contract
    for fetching private keys (local user only) and contact information.

    Core cryptographic responsibilities (Visa/Meta key pairs):
    1. Encryption        : Use Visa public key (terminal-specific) or Meta key (fallback)
    2. Decryption        : Use private keys paired with Visa/Meta public keys
    3. Signing           : Use private key paired with Visa/Meta public key
    4. Verification      : Use Visa/Meta public keys
    5. Visa Signing      : Use private key paired with Meta public key (only)
    6. Visa Verification : Use Meta public key (only)
    """

    @abstractmethod
    async def get_contacts(self, identifier: ID) -> List[ID]:
        """
        Get user's contacts list

        :param identifier: user ID
        :return: contact ID list
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.get_contacts()'
        )

    @abstractmethod
    async def private_keys_for_decryption(self, identifier: ID) -> List[DecryptKey]:
        """
        Get user's private keys for decryption
        (which paired with [visa.key, meta.key])

        :param identifier: user ID
        :return: private keys
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.private_keys_for_decryption()'
        )

    @abstractmethod
    async def private_key_for_signature(self, identifier: ID) -> Optional[SignKey]:
        """
        Get user's private key for signature
        (which paired with visa.key or meta.key)

        :param identifier: user ID
        :return: private key
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.private_key_for_signature()'
        )

    @abstractmethod
    async def private_key_for_visa_signature(self, identifier: ID) -> Optional[SignKey]:
        """
        Get user's private key for signing visa

        :param identifier: user ID
        :return: private key
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.private_key_for_visa_signature()'
        )


class User(Entity, ABC):
    """User account interface for secure communication (with Visa terminal support).

    Extends :class:`Entity` with user-specific cryptographic operations, contact management,
    and Visa-based terminal encryption.

    Supports core secure communication functions:
      1. Verification : Verify message signatures using Meta/Visa public keys
      2. Encryption   : Encrypt data for specific user terminals (via EncryptedBundle)
      3. Signing      : Generate message signatures (local user only)
      4. Decryption   : Decrypt terminal-specific data (local user only)
    """

    # @property
    # @abstractmethod
    # def data_source(self) -> Optional[UserDataSource]:
    #     raise NotImplementedError(
    #         f'Not implemented: {type(self).__module__}.{type(self).__name__}.data_source getter'
    #     )
    #
    # @data_source.setter
    # @abstractmethod
    # def data_source(self, delegate: UserDataSource):
    #     raise NotImplementedError(
    #         f'Not implemented: {type(self).__module__}.{type(self).__name__}.data_source setter'
    #     )

    @property
    @abstractmethod
    async def contacts(self) -> List[ID]:
        """
        Get all contacts of the user

        :return: contacts list
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.contacts getter'
        )

    @property
    @abstractmethod
    async def terminals(self) -> Set[str]:
        """
        Get terminals from visa documents

        :return: login devices
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.terminals getter'
        )

    @abstractmethod
    async def verify(self, data: bytes, signature: bytes) -> bool:
        """
        Verify data and signature with user's public keys

        :param data:
        :param signature:
        :return:
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.verify()'
        )

    @abstractmethod
    async def encrypt_bundle(self, data: bytes) -> EncryptedBundle:
        """
        Encrypt data, try visa.key first, if not found, use meta.key

        :param data: serialized symmetric key info
        :return: EncryptedBundle with terminal-specific encrypted data
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.encrypt_bundle()'
        )

    #
    #   interfaces for local user
    #

    @abstractmethod
    async def sign(self, data: bytes) -> bytes:
        """
        Sign data with user's private key

        :param data: message data
        :return: signature
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.sign()'
        )

    @abstractmethod
    async def decrypt_bundle(self, bundle: EncryptedBundle) -> Optional[bytes]:
        """
        Decrypt data with user's private key(s)

        :param bundle: Encrypted data bundle with terminal-specific data
        :return: serialized symmetric key info
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.decrypt_bundle()'
        )

    #
    #   Interfaces for Visa Document
    #

    @abstractmethod
    async def sign_document(self, document: Document) -> Optional[Document]:
        # NOTICE: only sign visa document with the private key paired with your meta.key
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.sign_document()'
        )

    @abstractmethod
    async def verify_document(self, document: Document) -> bool:
        # NOTICE: only verify visa document with meta.key
        #         (if meta not exists, user won't be created)
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.verify_document()'
        )


class BaseUser(BaseEntity, User):

    # def __init__(self, identifier: ID):
    #     super().__init__(identifier=identifier)

    @BaseEntity.data_source.getter  # Override
    def data_source(self) -> Optional[UserDataSource]:
        return super().data_source

    # @data_source.setter  # Override
    # def data_source(self, facebook: UserDataSource):
    #     super(BaseUser, BaseUser).data_source.__set__(self, facebook)

    @property  # Override
    async def contacts(self) -> List[ID]:
        facebook = self.data_source
        assert isinstance(facebook, UserDataSource), f'user data source error: {facebook}'
        return await facebook.get_contacts(identifier=self.identifier)

    @property  # Override
    async def terminals(self) -> Set[str]:
        docs = await self.documents
        assert len(docs) > 0, f'failed to get documents: {self.identifier}'
        agent = visa_agent()
        return agent.get_terminals(documents=docs)

    # Override
    async def verify(self, data: bytes, signature: bytes) -> bool:
        meta = await self.meta
        docs = await self.documents
        agent = visa_agent()
        keys = agent.get_verify_keys(meta=meta, documents=docs)
        assert len(keys) > 0, f'failed to get verify keys: {self.identifier}'
        for key in keys:
            if key.verify(data=data, signature=signature):
                # matched!
                return True
        # signature not match
        # TODO: check whether visa is expired, query new document for this contact
        return False

    # Override
    async def encrypt_bundle(self, data: bytes) -> EncryptedBundle:
        # NOTICE: meta.key will never changed, so use visa.key to encrypt message
        #         is the better way
        meta = await self.meta
        docs = await self.documents
        agent = visa_agent()
        return agent.encrypt_bundle(data=data, meta=meta, documents=docs)

    # Override
    async def sign(self, data: bytes) -> bytes:
        key = await self._private_key_for_signature()
        assert key is not None, f'failed to get sign key for user: {self.identifier}'
        return key.sign(data=data)

    # Override
    async def decrypt_bundle(self, bundle: EncryptedBundle) -> Optional[bytes]:
        # NOTICE: if you provide a public key in visa document for encryption,
        #         here you should return the private key paired with visa.key
        dictionary = bundle.to_map()
        assert len(dictionary) > 0, f'key data empty: {bundle}'
        for terminal, ciphertext in dictionary.items():
            # get private keys for terminal
            decrypt_keys = await self._private_keys_for_decryption(terminal=terminal)
            if decrypt_keys is None:
                # assert False, f'failed to get decrypt keys for user: {self.identifier}, terminal: {terminal}'
                continue
            # try decrypting it with each private key
            for pri_key in decrypt_keys:
                plaintext = pri_key.decrypt(ciphertext=ciphertext)
                if plaintext is not None and len(plaintext) > 0:
                    # OK
                    return plaintext
        # decryption failed
        # TODO: check whether my visa key is changed, push new visa to this contact
        return None

    # Override
    async def sign_document(self, document: Document) -> Optional[Document]:
        uid = self.identifier
        helper = account_handler()
        info = document.to_map()
        did = helper.get_document_id(document=info)
        assert did is None or did.is_same_as(other=uid), f'visa ID not match: {did}, {uid}'
        # NOTICE: only sign visa with the private key paired with your meta.key
        pri_key = await self._private_key_for_visa_signature()
        if pri_key is None:
            # assert False, f'failed to get sign key for visa: {uid}'
            return None
        if document.sign(private_key=pri_key) is None:
            # assert False, f'failed to sign visa: {self.identifier}, {document}'
            return None
        # OK
        return document

    # Override
    async def verify_document(self, document: Document) -> bool:
        # NOTICE: only verify visa with meta.key
        #         (if meta not exists, user won't be created)
        uid = self.identifier
        helper = account_handler()
        info = document.to_map()
        did = helper.get_document_id(document=info)
        assert did is None or did.is_same_as(other=uid), f'visa ID not match: {did}, {uid}'
        # if meta not exists, user won't be created
        meta = await self.meta
        key = meta.public_key
        assert key is not None, f'failed to get meta key for visa: {uid}'
        return document.verify(public_key=key)

    #
    #   Private Keys
    #

    # protected
    async def _private_keys_for_decryption(self, terminal: str) -> List[DecryptKey]:
        """Retrieves the decryption private keys for a specific terminal (async).

        Queries the :class:`UserDataSource` for private keys paired with the public keys
        in the user's Visa/Meta documents, targeting the given terminal.

        The ``terminal`` is the device terminal string (empty or "/" for wildcard).

        Returns the list of decryption private keys (null if data source is missing).
        """
        facebook = self.data_source
        assert isinstance(facebook, UserDataSource), f'user data source error: {facebook}'
        uid = self.identifier
        if terminal == '' or terminal == '/':
            uid = uid.without_terminal()
        else:
            uid = uid.with_terminal(terminal=terminal)
            assert terminal != '*', f'terminal should not be "*"'
        return await facebook.private_keys_for_decryption(identifier=uid)

    # protected
    async def _private_key_for_signature(self) -> Optional[SignKey]:
        """Retrieves the private key for message signing (async).

        Returns the private key paired with the user's Visa/Meta public key,
        used to generate digital signatures for outgoing messages.

        Returns the signing key (null if data source is missing).
        """
        facebook = self.data_source
        assert isinstance(facebook, UserDataSource), f'user data source error: {facebook}'
        uid = self.identifier
        return await facebook.private_key_for_signature(identifier=uid)

    # protected
    async def _private_key_for_visa_signature(self) -> Optional[SignKey]:
        """Retrieves the private key for Visa document signing (async).

        Returns the private key paired with the user's Meta public key (only),
        used to sign the user's Visa documents (identity verification).

        Returns the signing key for Visa documents (null if data source is missing).
        """
        facebook = self.data_source
        assert isinstance(facebook, UserDataSource), f'user data source error: {facebook}'
        uid = self.identifier
        return await facebook.private_key_for_visa_signature(identifier=uid)
