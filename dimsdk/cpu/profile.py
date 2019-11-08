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
from dimp import InstantMessage
from dimp import Content
from dimp import TextContent, Command, ProfileCommand

from ..protocol import ReceiptCommand

from .command import CommandProcessor


class ProfileCommandProcessor(CommandProcessor):

    def __get(self, identifier: ID) -> Content:
        # querying profile for ID
        self.info('search meta %s' % identifier)
        profile = self.facebook.profile(identifier=identifier)
        # response
        if profile is not None:
            return ProfileCommand.response(identifier=identifier, profile=profile)
        else:
            return TextContent.new(text='Sorry, profile for %s not found.' % identifier)

    def __put(self, identifier: ID, meta: Meta, profile: Profile) -> Content:
        if meta is not None:
            # received a meta for ID
            if self.facebook.save_meta(identifier=identifier, meta=meta):
                self.info('meta saved %s, %s' % (identifier, meta))
            else:
                self.error('meta not match %s, %s' % (identifier, meta))
                return TextContent.new(text='Meta not match %s!' % identifier)
        # received a new profile for ID
        self.info('received profile %s' % identifier)
        if self.facebook.save_profile(profile=profile):
            self.info('profile saved %s' % profile)
            return ReceiptCommand.new(message='Profile of %s received!' % identifier)
        else:
            self.error('profile not valid %s' % profile)
            return TextContent.new(text='Profile signature not match %s!' % identifier)

    #
    #   main
    #
    def process(self, content: Content, sender: ID, msg: InstantMessage) -> Optional[Content]:
        assert isinstance(content, ProfileCommand), 'command error: %s' % content
        identifier = self.facebook.identifier(content.identifier)
        meta = content.meta
        profile = content.profile
        if profile is None:
            return self.__get(identifier=identifier)
        else:
            return self.__put(identifier=identifier, meta=meta, profile=profile)


# register
CommandProcessor.register(command=Command.PROFILE, processor_class=ProfileCommandProcessor)
