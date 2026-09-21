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

from typing import Union

from dimp import MessageExtensions
from dimp import shared_message_extensions

from .instant_delegate import InstantMessageDelegate
from .secure_delegate import SecureMessageDelegate
from .reliable_delegate import ReliableMessageDelegate

from .instant_packer import InstantMessagePacker
from .secure_packer import SecureMessagePacker
from .reliable_packer import ReliableMessagePacker


# noinspection PyMethodMayBeStatic
class MessagePackerFactory:
    """Factory for creating message packers.

    Provides creation methods for the three message packers
    (instant/secure/reliable), which can be overridden by subclasses.
    """

    def create_instant_message_packer(self, messenger: InstantMessageDelegate):
        """Creates an :class:`InstantMessagePacker` for the given delegate.

        `delegate` is the instant message delegate (encryption pipeline).

        Returns a new :class:`InstantMessagePacker` instance.
        """
        return InstantMessagePacker(messenger=messenger)

    def create_secure_message_packer(self, messenger: SecureMessageDelegate):
        """Creates a :class:`SecureMessagePacker` for the given delegate.

        `delegate` is the secure message delegate (decryption/signing pipeline).

        Returns a new :class:`SecureMessagePacker` instance.
        """
        return SecureMessagePacker(messenger=messenger)

    def create_reliable_message_packer(self, messenger: ReliableMessageDelegate):
        """Creates a :class:`ReliableMessagePacker` for the given delegate.

        `delegate` is the reliable message delegate (verification pipeline).

        Returns a new :class:`ReliableMessagePacker` instance.
        """
        return ReliableMessagePacker(messenger=messenger)


# -----------------------------------------------------------------------------
#  Message Extensions
# -----------------------------------------------------------------------------


class MessagePackerExtension:
    """MessagePacker Extensions

    Global :class:`MessagePackerFactory` instance (shared singleton) for creating
    message packers, accessible via :class:`MessageExtensions`.
    """

    @property
    def packer_factory(self) -> MessagePackerFactory:
        """The shared :class:`MessagePackerFactory` instance (getter)."""
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.packer_factory getter'
        )

    @packer_factory.setter
    def packer_factory(self, factory: MessagePackerFactory):
        """Replaces the shared :class:`MessagePackerFactory` instance (setter)."""
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.packer_factory setter'
        )


shared_message_extensions.packer_factory = MessagePackerFactory()


def _message_extension() -> Union[MessagePackerExtension, MessageExtensions]:
    return shared_message_extensions


def packer_factory() -> MessagePackerFactory:
    ext = _message_extension()
    return ext.packer_factory
