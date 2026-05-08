# -*- coding: utf-8 -*-
#
#   DIMP : Decentralized Instant Messaging Protocol
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

from dimp import shared_message_extensions

from .instant_delegate import InstantMessageDelegate
from .secure_delegate import SecureMessageDelegate
from .reliable_delegate import ReliableMessageDelegate

from .instant_packer import InstantMessagePacker
from .secure_packer import SecureMessagePacker
from .reliable_packer import ReliableMessagePacker


# noinspection PyMethodMayBeStatic
class MessagePackerFactory:

    def create_instant_message_packer(self, messenger: InstantMessageDelegate):
        return InstantMessagePacker(messenger=messenger)

    def create_secure_message_packer(self, messenger: SecureMessageDelegate):
        return SecureMessagePacker(messenger=messenger)

    def create_reliable_message_packer(self, messenger: ReliableMessageDelegate):
        return ReliableMessagePacker(messenger=messenger)


# -----------------------------------------------------------------------------
#  Message Extensions
# -----------------------------------------------------------------------------


class MessagePackerExtension:

    @property
    def packer_factory(self) -> MessagePackerFactory:
        """ Get message packer factory """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.packer_factory getter'
        )

    @packer_factory.setter
    def packer_factory(self, factory: MessagePackerFactory):
        """ Set message packer factory """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.packer_factory setter'
        )


shared_message_extensions.packer_factory = MessagePackerFactory()


def message_extensions() -> MessagePackerExtension:
    return shared_message_extensions


def packer_factory() -> MessagePackerFactory:
    ext = message_extensions()
    return ext.packer_factory
