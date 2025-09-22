# -*- coding: utf-8 -*-
#
#   DIM-SDK : Decentralized Instant Messaging Software Development Kit
#
#                                Written in 2022 by Moky <albert.moky@gmail.com>
#
# ==============================================================================
# MIT License
#
# Copyright (c) 2022 Albert Moky
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
from typing import Optional, List, Dict

from dimp import ID
from dimp import ReliableMessage
from dimp import Envelope, Content
from dimp import ReceiptCommand
from dimp import CustomizedContent

from ..twins import TwinsHelper
from ..facebook import Facebook
from ..messenger import Messenger

from .base import BaseContentProcessor


class CustomizedContentHandler(ABC):
    """
        Handler for Customized Content
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    @abstractmethod
    async def handle_action(self, act: str, sender: ID, content: CustomizedContent,
                            msg: ReliableMessage) -> List[Content]:
        """
        Do your job

        @param act:     action
        @param sender:  user ID
        @param content: customized content
        @param msg:     network message
        @return contents
        """
        raise NotImplemented


class BaseCustomizedHandler(TwinsHelper, CustomizedContentHandler):
    """
        Default Handler
        ~~~~~~~~~~~~~~~
    """

    # Override
    async def handle_action(self, act: str, sender: ID, content: CustomizedContent,
                            msg: ReliableMessage) -> List[Content]:
        app = content.application
        mod = content.module
        text = 'Content not support.'
        return self._respond_receipt(text=text, content=content, envelope=msg.envelope, extra={
            'template': 'Customized content (app: ${app}, mod: ${mod}, act: ${act}) not support yet!',
            'replacements': {
                'app': app,
                'mod': mod,
                'act': act,
            }
        })

    #
    #   Convenient responding
    #

    # noinspection PyMethodMayBeStatic
    def _respond_receipt(self, text: str, envelope: Envelope, content: Optional[Content],
                         extra: Optional[Dict] = None) -> List[ReceiptCommand]:
        return [
            # create base receipt command with text & original envelope
            BaseContentProcessor.create_receipt(text=text, envelope=envelope, content=content, extra=extra)
        ]


class CustomizedContentProcessor(BaseContentProcessor):
    """
        Customized Content Processing Unit
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        Handle content for application customized
    """

    def __init__(self, facebook: Facebook, messenger: Messenger):
        super().__init__(facebook=facebook, messenger=messenger)
        self.__default_handler = self._create_default_handler(facebook=facebook, messenger=messenger)

    # noinspection PyMethodMayBeStatic
    def _create_default_handler(self, facebook: Facebook, messenger: Messenger) -> CustomizedContentHandler:
        return BaseCustomizedHandler(facebook=facebook, messenger=messenger)

    @property  # protected
    def default_handler(self) -> CustomizedContentHandler:
        return self.__default_handler

    # Override
    async def process_content(self, content: Content, r_msg: ReliableMessage) -> List[Content]:
        assert isinstance(content, CustomizedContent), 'customized content error: %s' % content
        # get handler for 'app' & 'mod'
        app = content.application
        mod = content.module
        handler = self._filter(app=app, mod=mod, content=content, msg=r_msg)
        # handle the action
        act = content.action
        sender = r_msg.sender
        return await handler.handle_action(act, sender=sender, content=content, msg=r_msg)

    # noinspection PyUnusedLocal
    def _filter(self, app: str, mod: str, content: CustomizedContent, msg: ReliableMessage) -> CustomizedContentHandler:
        """ Override for your handler """
        # if the application has too many modules, I suggest you to
        # use different handler to do the job for each module.
        return self.default_handler
