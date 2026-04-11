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
from typing import Optional, Any, Dict
from typing import Iterator, Iterable, ItemsView, KeysView, ValuesView

from dimp import base64_encode
from dimp import TransportableData
from dimp import ID, Identifier
from dimp import AccountExtensions, shared_account_extensions


class EncryptedBundle(ABC):

    @property
    @abstractmethod
    def string(self) -> str:
        raise NotImplemented

    @property
    @abstractmethod
    def dictionary(self) -> Dict[str, bytes]:
        raise NotImplemented

    @property
    @abstractmethod
    def empty(self) -> bool:
        raise NotImplemented

    @abstractmethod
    def clear(self):
        """ D.clear() -> None.  Remove all items from D. """
        raise NotImplemented

    @abstractmethod
    def get(self, key: str, default: Optional[bytes] = None) -> Optional[bytes]:
        """ Return the value for key if key is in the dictionary, else default. """
        raise NotImplemented

    @abstractmethod
    def items(self) -> ItemsView[str, bytes]:
        """ D.items() -> a set-like object providing a view on D's items """
        raise NotImplemented

    @abstractmethod
    def keys(self) -> KeysView[str]:
        """ D.keys() -> a set-like object providing a view on D's keys """
        raise NotImplemented

    @abstractmethod
    def pop(self, key: str, default: Optional[bytes] = None) -> Optional[bytes]:
        """
        D.pop(k[,d]) -> v, remove specified key and return the corresponding value.
        If key is not found, d is returned if given, otherwise KeyError is raised
        """
        raise NotImplemented

    @abstractmethod
    def values(self) -> ValuesView[bytes]:
        """ D.values() -> an object providing a view on D's values """
        raise NotImplemented

    def __contains__(self, o) -> bool:
        """ True if the dictionary has the specified key, else False. """
        raise NotImplemented

    def __delitem__(self, v: str):
        """ Delete self[key]. """
        raise NotImplemented

    def __getitem__(self, k: str) -> bytes:
        """ x.__getitem__(y) <==> x[y] """
        raise NotImplemented

    def __iter__(self) -> Iterator[str]:
        """ Implement iter(self). """
        raise NotImplemented

    def __len__(self) -> int:
        """ Return len(self). """
        raise NotImplemented

    def __str__(self) -> str:
        """ Return str(self). """
        raise NotImplemented

    def __repr__(self) -> str:
        """ Return repr(self). """
        raise NotImplemented

    def __setitem__(self, k: str, v: Optional[bytes]):
        """ Set self[key] to value. """
        raise NotImplemented

    def __sizeof__(self) -> int:
        """ D.__sizeof__() -> size of D in memory, in bytes """
        raise NotImplemented

    __hash__ = None

    @abstractmethod
    def encode(self, identifier: ID) -> Dict[str, Any]:
        raise NotImplemented

    @classmethod
    def decode(cls, keys: Dict, identifier: ID, terminals: Iterable[str]):  # -> EncryptedBundle:
        helper = bundle_helper()
        return helper.decode_bundle(keys=keys, identifier=identifier, terminals=terminals)


class UserEncryptedBundle(EncryptedBundle):

    def __init__(self):
        super().__init__()
        self.__dictionary: Dict[str, bytes] = {}

    @property  # Override
    def string(self) -> str:
        clazz = self.__class__.__name__
        text = ''
        info = self.__dictionary
        for key in info:
            value = info.get(key)
            text += '\t"%s": %d byte(s)\n' % (key, len(value))
        return '<%s count=%d>\n%s</%s>' % (clazz, len(info), text, clazz)

    @property  # Override
    def dictionary(self) -> Dict[str, bytes]:
        return self.__dictionary

    @property  # Override
    def empty(self) -> bool:
        return len(self.__dictionary) == 0

    # Override
    def clear(self):
        self.__dictionary.clear()

    # Override
    def get(self, key: str, default: Optional[bytes] = None) -> Optional[bytes]:
        return self.__dictionary.get(key, default)

    # Override
    def items(self) -> ItemsView[str, bytes]:
        return self.__dictionary.items()

    # Override
    def keys(self) -> KeysView[str]:
        return self.__dictionary.keys()

    # Override
    def pop(self, key: str, default: Optional[bytes] = None) -> Optional[bytes]:
        return self.__dictionary.pop(key, default)

    # Override
    def values(self) -> ValuesView[bytes]:
        return self.__dictionary.values()

    # Override
    def __contains__(self, o) -> bool:
        """ True if the dictionary has the specified key, else False. """
        return self.__dictionary.__contains__(o)

    # Override
    def __delitem__(self, v: str):
        """ Delete self[key]. """
        self.__dictionary.__delitem__(v)

    # Override
    def __getitem__(self, k: str) -> bytes:
        """ x.__getitem__(y) <==> x[y] """
        return self.__dictionary.__getitem__(k)

    # Override
    def __iter__(self) -> Iterator[str]:
        """ Implement iter(self). """
        return self.__dictionary.__iter__()

    # Override
    def __len__(self) -> int:
        """ Return len(self). """
        return self.__dictionary.__len__()

    # Override
    def __str__(self) -> str:
        """ Return str(self). """

    # Override
    def __repr__(self) -> str:
        """ Return repr(self). """
        return self.__dictionary.__repr__()

    # Override
    def __setitem__(self, k: str, v: Optional[bytes]):
        """ Set self[key] to value. """
        self.__dictionary.__setitem__(k, v)

    # Override
    def __sizeof__(self) -> int:
        """ D.__sizeof__() -> size of D in memory, in bytes """
        return self.__dictionary.__sizeof__()

    # Override
    def encode(self, identifier: ID) -> Dict[str, Any]:
        helper = bundle_helper()
        return helper.encode_bundle(bundle=self, identifier=identifier)


def bundle_helper():
    helper = shared_account_extensions.bundle_helper
    assert isinstance(helper, EncryptedBundleHelper), 'bundle helper error: %s' % helper
    return helper


# -----------------------------------------------------------------------------
#  Account Extensions
# -----------------------------------------------------------------------------


class EncryptedBundleHelper(ABC):

    @abstractmethod
    def encode_bundle(self, bundle: EncryptedBundle, identifier: ID) -> Dict[str, Any]:
        raise NotImplemented

    @abstractmethod
    def decode_bundle(self, keys: Dict, identifier: ID, terminals: Iterable[str]) -> EncryptedBundle:
        raise NotImplemented


class DefaultBundleHelper(EncryptedBundleHelper):

    # Override
    def encode_bundle(self, bundle: EncryptedBundle, identifier: ID) -> Dict[str, Any]:
        text = Identifier.concat(name=identifier.name, address=identifier.address)
        encoded_keys = {}
        info = bundle.dictionary
        for terminal in info:
            data = info.get(terminal)
            # encode data
            base64 = base64_encode(data=data)
            if terminal == '' or terminal == '*':
                target = text
            else:
                target = '%s/%s' % (text, terminal)
            # insert to 'message.keys' with ID + terminal
            encoded_keys[target] = base64
        # OK
        return encoded_keys

    # Override
    def decode_bundle(self, keys: Dict, identifier: ID, terminals: Iterable[str]) -> EncryptedBundle:
        bundle = UserEncryptedBundle()
        #
        #  0. ID string without terminal (base identifier)
        #
        text = Identifier.concat(name=identifier.name, address=identifier.address)
        for item in terminals:
            if item == '':
                target = '*'
            else:
                target = item
            #
            #  1. Get encoded data for target (ID + terminal)
            #    - Wildcard (*) uses base ID without terminal suffix
            #    - Specific terminals use "ID/terminal" format
            #
            if target == '*':
                base64 = keys.get(text)
            else:
                base64 = keys.get('%s/%s' % (text, target))
            if base64 is None:
                # Key data not found for this terminal - skip
                continue
            #
            #  2. Decode base64 data to raw bytes
            #
            ted = TransportableData.parse(base64)
            if ted is not None:
                data = ted.binary
                if data is not None:
                    #
                    #  3. Store decoded data for the terminal
                    #
                    bundle[target] = data
                # else:
                #     assert False, 'key data error: %s -> %s' % (item, base64)
        # OK
        return bundle


class _BundleExt:
    _bundle_helper: EncryptedBundleHelper = DefaultBundleHelper()

    @property
    def bundle_helper(self) -> EncryptedBundleHelper:
        return _BundleExt._bundle_helper

    @bundle_helper.setter
    def bundle_helper(self, helper: EncryptedBundleHelper):
        _BundleExt._bundle_helper = helper


AccountExtensions.bundle_helper = _BundleExt.bundle_helper
