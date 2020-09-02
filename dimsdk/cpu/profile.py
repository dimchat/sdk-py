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
    Profile Command Processor
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from typing import Optional

from dimp import ID, Meta, Profile
from dimp import ReliableMessage
from dimp import Content
from dimp import TextContent, Command, ProfileCommand

from ..protocol import ReceiptCommand

from .command import CommandProcessor


class ProfileCommandProcessor(CommandProcessor):

    def __get(self, identifier: ID) -> Content:
        facebook = self.facebook
        # query profile for ID
        profile: Profile = facebook.profile(identifier=identifier)
        if profile is None or 'data' not in profile:
            # profile not found
            return TextContent.new(text='Sorry, profile for %s not found.' % identifier)
        # response
        meta: Meta = facebook.meta(identifier=identifier)
        return ProfileCommand.response(identifier=identifier, profile=profile, meta=meta)

    def __put(self, identifier: ID, meta: Meta, profile: Profile) -> Content:
        facebook = self.facebook
        if meta is not None:
            # received a meta for ID
            if not facebook.verify_meta(meta=meta, identifier=identifier):
                # meta not match
                return TextContent.new(text='Meta not match ID: %s' % identifier)
            if not facebook.save_meta(meta=meta, identifier=identifier):
                # save meta failed
                return TextContent.new(text='Meta not accept: %s!' % identifier)
        # received a new profile for ID
        if not facebook.verify_profile(profile=profile, identifier=identifier):
            # profile signature not match
            return TextContent.new(text='Profile not match ID: %s' % identifier)
        if not facebook.save_profile(profile=profile):
            # save profile failed
            return TextContent.new(text='Profile not accept: %s!' % identifier)
        # response
        return ReceiptCommand.new(message='Profile received: %s' % identifier)

    #
    #   main
    #
    def process(self, content: Content, sender: ID, msg: ReliableMessage) -> Optional[Content]:
        assert isinstance(content, ProfileCommand), 'command error: %s' % content
        identifier = content.identifier
        profile = content.profile
        if profile is None:
            return self.__get(identifier=identifier)
        else:
            # check meta
            meta = content.meta
            return self.__put(identifier=identifier, meta=meta, profile=profile)


# register
CommandProcessor.register(command=Command.PROFILE, processor_class=ProfileCommandProcessor)
