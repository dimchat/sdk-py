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

from dimp import Meta, Document
from dimp import ID, SecureMessage

from dimp import EncryptedBundle, UserEncryptedBundle
from dimp import AccountExtensions
from dimp import shared_account_extensions, account_handler


# -----------------------------------------------------------------------------
#  Visa Agent (Visa-based Encryption/Verification)
# -----------------------------------------------------------------------------


class VisaAgent(ABC):
    """Agent interface for Visa-based cryptographic operations.

    Provides core functionality for working with user Visa documents:
    - Encrypting data for multiple user terminals using Visa/Meta public keys
    - Extracting verification keys from Meta/Visa documents
    - Collecting terminal identifiers from Visa documents

    Acts as a helper to abstract complex Visa-based encryption logic from User entity.
    """

    @abstractmethod
    def decode_bundle(self, s_msg: SecureMessage, receiver: ID) -> Optional[EncryptedBundle]:
        """Decrypts key bundle for the receiver.

        `s_msg` is the received message.
        `receiver` is the actual receiver (user, or group member).

        Returns the encrypted bundle with terminals.
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.decode_bundle()'
        )

    @abstractmethod
    def encrypt_bundle(self, data: bytes, meta: Meta, documents: List[Document]) -> EncryptedBundle:
        """Encrypts plaintext data using all available Visa/Meta public keys.

        Creates an :class:`EncryptedBundle` with terminal-specific encrypted data, using:
        1. Visa public keys for terminal-specific encryption
        2. Meta public key as fallback for wildcard (*) encryption

        `data` is the raw data to encrypt (usually a symmetric message key).
        `meta` is the user's core Meta (contains fallback public key).
        `documents` is the list of user Visa documents (contains terminal-specific public keys).

        Returns an EncryptedBundle with terminal-specific encrypted data.
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.encrypt_bundle()'
        )

    @abstractmethod
    def get_verify_keys(self, meta: Meta, documents: List[Document]) -> List[VerifyKey]:
        """Extracts all verification keys from Meta and Visa documents.

        Collects public verification keys from:
        1. User's Meta (core identity key)
        2. All Visa documents (terminal-specific keys)

        `meta` is the user's core Meta.
        `documents` is the list of user Visa documents.

        Returns the list of VerifyKey instances for signature verification.
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.get_verify_keys()'
        )

    @abstractmethod
    def get_terminals(self, documents: List[Document]) -> Set[str]:
        """Extracts all terminal identifiers from user Visa documents.

        Collects unique terminal strings (e.g., "mobile", "desktop") from Visa documents,
        representing all devices the user is logged into.

        `documents` is the list of user Visa documents.

        Returns the set of unique terminal identifiers (empty set if none).
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.get_terminals()'
        )


# noinspection PyMethodMayBeStatic
class DefaultVisaAgent(VisaAgent):

    # Override
    def decode_bundle(self, s_msg: SecureMessage, receiver: ID) -> Optional[EncryptedBundle]:
        # TODO: check key digest
        keys = s_msg.encrypted_keys
        if keys is None or len(keys) == 0:
            return None
        # TODO: get terminal(s) for local user
        terminal = receiver.terminal
        if terminal is None or len(terminal) == 0:
            # get full bundle
            return EncryptedBundle.decode(encoded_keys=keys, receiver=receiver, terminals=None)
        # get single bundle
        devices = {terminal}
        receiver = receiver.without_terminal()
        return EncryptedBundle.decode(encoded_keys=keys, receiver=receiver, terminals=devices)

    # Override
    def encrypt_bundle(self, data: bytes, meta: Meta, documents: List[Document]) -> EncryptedBundle:
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
            # if (terminal is None || terminal.isEmpty) {
            #   terminal = '/';
            # }
            if bundle.get(terminal) is not None:
                # assert False, f'duplicated visa key: {doc}'
                continue
            ciphertext = pub_key.encrypt(plaintext=data)
            bundle[terminal] = ciphertext
        if bundle.is_empty:
            #
            #  2. encrypt with meta key
            #
            meta_key = meta.public_key
            if isinstance(meta_key, EncryptKey):
                # terminal = '/'
                ciphertext = meta_key.encrypt(plaintext=data)
                bundle['/'] = ciphertext
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
            #     assert False, f'failed to get visa key: {doc}'
        # the sender may use identity key to sign message.data,
        # try to verify it with meta.key too.
        verify_keys.append(meta.public_key)
        # OK
        return verify_keys

    # protected
    def get_verify_key(self, document: Document) -> Optional[VerifyKey]:
        """Extracts the public verification key from a user document (Visa).

        Parses the "key" property of the document as a :class:`PublicKey`.

        `document` is the user document (Visa) containing the public key.

        Returns the verification key (null if the document has no valid key).
        """
        # public key in user profile?
        key = document.get_property(name='key')
        return PublicKey.parse(key=key)

    # protected
    def get_encrypt_key(self, document: Document) -> Optional[EncryptKey]:
        """Extracts the public encryption key from a user document (Visa).

        Parses the "key" property of the document as a :class:`PublicKey`; only keys
        implementing :class:`EncryptKey` can be used for encryption.

        `document` is the user document (Visa) containing the public key.

        Returns the encryption key (null if not an encryptable key).
        """
        key = document.get_property(name='key')
        pub_key = PublicKey.parse(key=key)
        if pub_key is None:
            # profile document?
            return None
        elif isinstance(pub_key, EncryptKey):
            return pub_key
        # else:
        #     assert False, f'visa key error: {pub_key}'
        return None

    # protected
    def get_terminal(self, document: Document) -> str:
        """Determines the terminal identifier for a user document (Visa).

        Reads the "terminal" property from the document; if missing, extracts it
        from the document ID. Falls back to "/" (wildcard) when empty or "*".

        `document` is the user document (Visa) to get terminal from.

        Returns the terminal string ("/" for wildcard).
        """
        terminal = document.get_str(key='terminal')
        if terminal is None:
            # get from document ID
            helper = account_handler()
            info = document.to_map()
            did = helper.get_document_id(document=info)
            if did is not None:
                terminal = did.terminal
            # else:
            #     assert False, f'document ID not found: {document}'
            #     # TODO: get from property?
        if terminal is None or len(terminal) == 0 or terminal == '*':
            terminal = '/'
        return terminal

    # Override
    def get_terminals(self, documents: List[Document]) -> Set[str]:
        devices = set()
        for doc in documents:
            terminal = self.get_terminal(document=doc)
            # if (terminal is None || terminal.isEmpty) {
            #   terminal = '/';
            # }
            devices.add(terminal)
        # OK
        return devices


# -----------------------------------------------------------------------------
#  Account Extensions
# -----------------------------------------------------------------------------


class VisaAgentExtension:

    @property
    def visa_agent(self) -> VisaAgent:
        """ Get visa agent """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.visa_agent getter'
        )

    @visa_agent.setter
    def visa_agent(self, agent: VisaAgent):
        """ Set visa agent """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.visa_agent setter'
        )


shared_account_extensions.visa_agent: VisaAgent = DefaultVisaAgent()


def _account_extension() -> Union[VisaAgentExtension, AccountExtensions]:
    return shared_account_extensions


def visa_agent() -> VisaAgent:
    ext = _account_extension()
    return ext.visa_agent
