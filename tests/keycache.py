# -*- coding: utf-8 -*-

"""
    Symmetric Keys Cache
    ~~~~~~~~~~~~~~~~~~~~

    Manage keys for conversations
"""

from abc import abstractmethod
from typing import Optional

from dimp import SymmetricKey, ID
from dimsdk import CipherKeyDelegate
from dimsdk import PlainKey


class KeyCache(CipherKeyDelegate):

    def __init__(self):
        super().__init__()
        # memory cache
        self.__key_map = {}
        self.__dirty = False

    def reload(self) -> bool:
        """ Trigger for loading cipher key table """
        dictionary = self.load_keys()
        if dictionary is None:
            return False
        return self.update_keys(dictionary)

    def flush(self):
        """ Trigger for saving cipher key table """
        if self.__dirty and self.save_keys(self.__key_map):
            # keys saved
            self.__dirty = False

    @abstractmethod
    def save_keys(self, key_map: dict) -> bool:
        """
        Callback for saving cipher key table into local storage

        :param key_map: all cipher keys(with direction) from memory cache
        :return:        True on success
        """
        pass

    @abstractmethod
    def load_keys(self) -> Optional[dict]:
        """
        Load cipher key table from local storage

        :return: keys map
        """
        pass

    def update_keys(self, key_map: dict) -> bool:
        """
        Update cipher key table into memory cache

        :param key_map: cipher keys(with direction) from local storage
        :return:        False on nothing changed
        """
        changed = False
        for _from in key_map:
            sender = ID.parse(identifier=_from)
            table = key_map.get(_from)
            assert isinstance(table, dict), 'sender table error: %s, %s' % (_from, table)
            for _to in table:
                receiver = ID.parse(identifier=_to)
                pw = table.get(_to)
                key = SymmetricKey.parse(key=pw)
                # TODO: check whether exists an old key
                changed = True
                # cache key with direction
                self.__cache_cipher_key(key, sender, receiver)
        return changed

    def __cipher_key(self, sender: ID, receiver: ID) -> Optional[SymmetricKey]:
        table = self.__key_map.get(sender)
        if table is not None:
            return table.get(receiver)

    def __cache_cipher_key(self, key: SymmetricKey, sender: ID, receiver: ID):
        table = self.__key_map.get(sender)
        if table is None:
            table = {}
            self.__key_map[sender] = table
        else:
            old = table.get(receiver)
            if old is not None:
                # check whether same key exists
                equals = True
                assert isinstance(key, dict), 'key info error: %s' % key
                for k in key:
                    v1 = key.get(k)
                    v2 = old.get(k)
                    if v1 == v2:
                        continue
                    equals = False
                    break
                if equals:
                    # no need to update
                    return
        table[receiver] = key

    #
    #   CipherKeyDelegate
    #

    # TODO: override to check whether key expired for sending message
    def cipher_key(self, sender: ID, receiver: ID, generate: bool = False) -> Optional[SymmetricKey]:
        if receiver.is_broadcast:
            return SymmetricKey.generate(algorithm=PlainKey.PLAIN)
        # get key from cache
        key = self.__cipher_key(sender, receiver)
        if key is None and generate:
            key = SymmetricKey.generate(algorithm=SymmetricKey.AES)
            self.__cache_cipher_key(key=key, sender=sender, receiver=receiver)
        return key

    def cache_cipher_key(self, key: SymmetricKey, sender: ID, receiver: ID):
        if receiver.is_broadcast:
            return
        self.__cache_cipher_key(key, sender, receiver)
        self.__dirty = True
