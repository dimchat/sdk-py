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

from mkm import SymmetricKey, PrivateKey, PublicKey
from mkm import NetworkID, Address, ID, Meta, Profile
from mkm import Entity, IEntityDataSource
from mkm import User, LocalUser, IUserDataSource
from mkm import Group, IGroupDataSource

from dkd import Content, ContentType, ForwardContent
from dkd import Envelope, Message
from dkd import InstantMessage, SecureMessage, ReliableMessage
from dkd import IInstantMessageDelegate, ISecureMessageDelegate, IReliableMessageDelegate

from dimp import TextContent, FileContent, ImageContent, AudioContent, VideoContent
from dimp import Command, HistoryCommand, GroupCommand
from dimp import InviteCommand, ExpelCommand, JoinCommand, QuitCommand
from dimp import QueryCommand, ResetCommand
from dimp import HandshakeCommand, MetaCommand, ProfileCommand

from dimp import ICallback, ICompletionHandler, ITransceiverDelegate
from dimp import Barrack
from dimp import KeyCache
from dimp import Transceiver

from .protocol import ReceiptCommand
from .protocol import BlockCommand, MuteCommand

from .network import NetMsgHead, NetMsg
from .network import CASubject, CAValidity, CAData, CertificateAuthority
from .network import ServiceProvider, Station

name = 'DIM-SDK'

__author__ = 'Albert Moky'

__all__ = [

    #
    #   MingKeMing
    #

    # crypto
    'SymmetricKey', 'PrivateKey', 'PublicKey',

    # entity
    'NetworkID', 'Address', 'ID', 'Meta', 'Profile',
    'Entity', 'IEntityDataSource',
    'User', 'LocalUser', 'IUserDataSource',
    'Group', 'IGroupDataSource',

    #
    #   DaoKeDao
    #

    # message
    'Content', 'ContentType', 'ForwardContent',
    'Envelope', 'Message',

    # transform
    'InstantMessage', 'SecureMessage', 'ReliableMessage',
    'IInstantMessageDelegate', 'ISecureMessageDelegate', 'IReliableMessageDelegate',

    #
    #   DIMP
    #

    # protocol
    'TextContent', 'FileContent', 'ImageContent', 'AudioContent', 'VideoContent',
    'Command', 'HistoryCommand', 'GroupCommand',
    'InviteCommand', 'ExpelCommand', 'JoinCommand', 'QuitCommand',
    'QueryCommand', 'ResetCommand',
    'HandshakeCommand', 'MetaCommand', 'ProfileCommand',

    # core
    'ICallback', 'ICompletionHandler', 'ITransceiverDelegate',
    'Barrack',
    'KeyCache',
    'Transceiver',

    #
    #   DIM SDK
    #

    # protocol
    'ReceiptCommand',
    'BlockCommand', 'MuteCommand',

    # network
    'NetMsgHead', 'NetMsg',
    'CASubject', 'CAValidity', 'CAData', 'CertificateAuthority',
    'ServiceProvider', 'Station',
]
