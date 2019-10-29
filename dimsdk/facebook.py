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

from abc import abstractmethod
from typing import Optional

from dimp import NetworkID, ID, Meta, Profile, User, Group
from dimp import Barrack, LocalUser

from .ans import AddressNameService


class Facebook(Barrack):

    def __init__(self):
        super().__init__()
        self.ans: AddressNameService = None

    def nickname(self, identifier: ID) -> str:
        assert identifier.type.is_user(), 'ID error: %s' % identifier
        user = self.user(identifier=identifier)
        if user is not None:
            return user.name

    @staticmethod
    def verify_meta(meta: Meta, identifier: ID) -> bool:
        if meta is not None:
            return meta.match_identifier(identifier)

    def verify_profile(self, profile: Profile) -> bool:
        if profile is None:
            return False
        elif profile.valid:
            # already verified
            return True
        # try to verify the profile
        identifier = self.identifier(profile.identifier)
        if identifier.type.is_user() or identifier.type.value == NetworkID.Polylogue:
            # if this is a user profile,
            #     verify it with the user's meta.key
            # else if this is a polylogue profile,
            #     verify it with the founder's meta.key (which equals to the group's meta.key)
            meta = self.meta(identifier=identifier)
            if meta is not None:
                return profile.verify(public_key=meta.key)
        else:
            raise NotImplementedError('unsupported profile ID: %s' % profile)

    @abstractmethod
    def save_meta(self, meta: Meta, identifier: ID) -> bool:
        pass

    #
    #   SocialNetworkDataSource
    #
    def identifier(self, string: str) -> Optional[ID]:
        if string is None:
            return None
        if self.ans is not None:
            # try from ANS record
            identifier = self.ans.record(name=string)
            if identifier is not None:
                return identifier
        # get from barrack
        return super().identifier(string=string)

    def user(self, identifier: ID) -> Optional[User]:
        #  get from barrack cache
        user = super().user(identifier=identifier)
        if user is not None:
            return user
        # check meta and private key
        meta = self.meta(identifier=identifier)
        if meta is not None:
            key = self.private_key_for_signature(identifier=identifier)
            if key is None:
                user = User(identifier=identifier)
            else:
                user = LocalUser(identifier=identifier)
            # cache it in barrack
            self.cache_user(user=user)
            return user

    def group(self, identifier: ID) -> Optional[Group]:
        # get from barrack cache
        group = super().group(identifier=identifier)
        if group is not None:
            return group
        # check meta
        meta = self.meta(identifier=identifier)
        if meta is not None:
            group = Group(identifier=identifier)
            # cache it in barrack
            self.cache_group(group=group)
            return group
