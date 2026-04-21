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

from abc import ABC, abstractmethod
from typing import Optional, Set, List

from dimp import DecryptKey, SignKey
from dimp import ID
from dimp import Visa

from ..crypto import EncryptedBundle
from ..crypto.agent import visa_agent, account_helper

from .entity import EntityDataSource, Entity, BaseEntity


class UserDataSource(EntityDataSource, ABC):
    """ This interface is for getting information for user

        User Data Source
        ~~~~~~~~~~~~~~~~

        (Encryption/decryption)
        1. public key for encryption
           if visa.key not exists, means it is the same key with meta.key
        2. private keys for decryption
           the private keys paired with [visa.key, meta.key]

        (Signature/Verification)
        3. private key for signature
           the private key paired with visa.key or meta.key
        4. public keys for verification
           [visa.key, meta.key]

        (Visa Document)
        5. private key for visa signature
           the private key paired with meta.key
        6. public key for visa verification
           meta.key only
    """

    @abstractmethod
    async def get_contacts(self, identifier: ID) -> List[ID]:
        """
        Get user's contacts list

        :param identifier: user ID
        :return: contact ID list
        """
        raise NotImplemented

    @abstractmethod
    async def private_keys_for_decryption(self, identifier: ID) -> List[DecryptKey]:
        """
        Get user's private keys for decryption
        (which paired with [visa.key, meta.key])

        :param identifier: user ID
        :return: private keys
        """
        raise NotImplemented

    @abstractmethod
    async def private_key_for_signature(self, identifier: ID) -> Optional[SignKey]:
        """
        Get user's private key for signature
        (which paired with visa.key or meta.key)

        :param identifier: user ID
        :return: private key
        """
        raise NotImplemented

    @abstractmethod
    async def private_key_for_visa_signature(self, identifier: ID) -> Optional[SignKey]:
        """
        Get user's private key for signing visa

        :param identifier: user ID
        :return: private key
        """
        raise NotImplemented


class User(Entity, ABC):
    """ This class is for creating user

        User for communication
        ~~~~~~~~~~~~~~~~~~~~~~

        functions:
            (User)
            1. verify(data, signature) - verify (encrypted content) data and signature
            2. encrypt(data)           - encrypt (symmetric key) data
            (LocalUser)
            3. sign(data)    - calculate signature of (encrypted content) data
            4. decrypt(data) - decrypt (symmetric key) data
    """

    # @property
    # @abstractmethod
    # def data_source(self) -> Optional[UserDataSource]:
    #     raise NotImplemented
    #
    # @data_source.setter
    # @abstractmethod
    # def data_source(self, delegate: UserDataSource):
    #     raise NotImplemented

    @property
    @abstractmethod
    async def contacts(self) -> List[ID]:
        """
        Get all contacts of the user

        :return: contacts list
        """
        raise NotImplemented

    @property
    @abstractmethod
    async def terminals(self) -> Set[str]:
        """
        Get terminals from visa documents

        :return: login devices
        """
        raise NotImplemented

    @abstractmethod
    async def verify(self, data: bytes, signature: bytes) -> bool:
        """
        Verify data and signature with user's public keys

        :param data:
        :param signature:
        :return:
        """
        raise NotImplemented

    @abstractmethod
    async def encrypt_bundle(self, plaintext: bytes) -> EncryptedBundle:
        """
        Encrypt data, try visa.key first, if not found, use meta.key

        :param plaintext: serialized symmetric key info
        :return: EncryptedBundle with terminal-specific encrypted data
        """
        raise NotImplemented

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
        raise NotImplemented

    @abstractmethod
    async def decrypt_bundle(self, bundle: EncryptedBundle) -> Optional[bytes]:
        """
        Decrypt data with user's private key(s)

        :param bundle: Encrypted data bundle with terminal-specific data
        :return: serialized symmetric key info
        """
        raise NotImplemented

    #
    #   Interfaces for Visa
    #

    @abstractmethod
    async def sign_visa(self, visa: Visa) -> Optional[Visa]:
        # NOTICE: only sign visa with the private key paired with your meta.key
        raise NotImplemented

    @abstractmethod
    async def verify_visa(self, visa: Visa) -> bool:
        # NOTICE: only verify visa with meta.key
        #         (if meta not exists, user won't be created)
        raise NotImplemented


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
        assert isinstance(facebook, UserDataSource), 'user delegate error: %s' % facebook
        return await facebook.get_contacts(identifier=self.identifier)

    @property  # Override
    async def terminals(self) -> Set[str]:
        docs = await self.documents
        assert len(docs) > 0, 'failed to get documents: %s' % self.identifier
        agent = visa_agent()
        return agent.get_terminals(documents=docs)

    # Override
    async def verify(self, data: bytes, signature: bytes) -> bool:
        meta = await self.meta
        docs = await self.documents
        agent = visa_agent()
        keys = agent.get_verify_keys(meta=meta, documents=docs)
        assert len(keys) > 0, 'failed to get verify keys: %s' % self.identifier
        for key in keys:
            if key.verify(data=data, signature=signature):
                # matched!
                return True
        # signature not match
        # TODO: check whether visa is expired, query new document for this contact

    # Override
    async def encrypt_bundle(self, plaintext: bytes) -> EncryptedBundle:
        # NOTICE: meta.key will never changed, so use visa.key to encrypt message
        #         is the better way
        meta = await self.meta
        docs = await self.documents
        agent = visa_agent()
        return agent.encrypt_bundle(plaintext=plaintext, meta=meta, documents=docs)

    # Override
    async def sign(self, data: bytes) -> bytes:
        key = await self._private_key_for_signature()
        assert key is not None, 'failed to get sign key for user: %s' % self.identifier
        return key.sign(data=data)

    # Override
    async def decrypt_bundle(self, bundle: EncryptedBundle) -> Optional[bytes]:
        # NOTICE: if you provide a public key in visa document for encryption,
        #         here you should return the private key paired with visa.key
        dictionary = bundle.to_dict()
        assert len(dictionary) > 0, 'key data empty: %s' % bundle
        for terminal in dictionary:
            ciphertext = dictionary.get(terminal)
            # get private keys for terminal
            decrypt_keys = await self._private_keys_for_decryption(terminal=terminal)
            if decrypt_keys is None:
                # assert False, 'failed to get decrypt keys for user: %s, terminal: %s' % (self.identifier, terminal)
                continue
            # try decrypting it with each private key
            for pri_key in decrypt_keys:
                plaintext = pri_key.decrypt(ciphertext=ciphertext)
                if plaintext is not None and len(plaintext) > 0:
                    # OK
                    return plaintext
        # decryption failed
        # TODO: check whether my visa key is changed, push new visa to this contact

    # Override
    async def sign_visa(self, visa: Visa) -> Optional[Visa]:
        uid = self.identifier
        helper = account_helper()
        info = visa.to_dict()
        did = helper.get_document_id(document=info)
        assert did is None or did.address == uid.address, 'visa ID not match: %s, %s' % (did, uid)
        # NOTICE: only sign visa with the private key paired with your meta.key
        pri_key = await self._private_key_for_visa_signature()
        if pri_key is None:
            # assert False, 'failed to get sign key for visa: %s' % uid
            return None
        if visa.sign(private_key=pri_key) is None:
            # assert False, 'failed to sign visa: %s, %s' % (self.identifier, visa)
            return None
        # OK
        return visa

    # Override
    async def verify_visa(self, visa: Visa) -> bool:
        # NOTICE: only verify visa with meta.key
        #         (if meta not exists, user won't be created)
        uid = self.identifier
        helper = account_helper()
        info = visa.to_dict()
        did = helper.get_document_id(document=info)
        assert did is None or did.address == uid.address, 'visa ID not match: %s, %s' % (did, uid)
        # if meta not exists, user won't be created
        meta = await self.meta
        key = meta.public_key
        assert key is not None, 'failed to get meta key for visa: %s' % self.identifier
        return visa.verify(public_key=key)

    #
    #   Private Keys
    #

    # protected
    async def _private_keys_for_decryption(self, terminal: str) -> List[DecryptKey]:
        facebook = self.data_source
        assert isinstance(facebook, UserDataSource), 'user delegate error: %s' % facebook
        uid = self.identifier
        if terminal is not None and len(terminal) > 0 and terminal != '*':
            uid = ID.create(name=uid.name, address=uid.address, terminal=terminal)
        return await facebook.private_keys_for_decryption(identifier=uid)

    # protected
    async def _private_key_for_signature(self) -> Optional[SignKey]:
        facebook = self.data_source
        assert isinstance(facebook, UserDataSource), 'user delegate error: %s' % facebook
        uid = self.identifier
        return await facebook.private_key_for_signature(identifier=uid)

    # protected
    async def _private_key_for_visa_signature(self) -> Optional[SignKey]:
        facebook = self.data_source
        assert isinstance(facebook, UserDataSource), 'user delegate error: %s' % facebook
        uid = self.identifier
        return await facebook.private_key_for_visa_signature(identifier=uid)
