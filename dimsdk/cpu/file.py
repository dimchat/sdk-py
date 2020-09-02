# -*- coding: utf-8 -*-
#
#   DIM-SDK : Decentralized Instant Messaging Software Development Kit
#
#                                Written in 2020 by Moky <albert.moky@gmail.com>
#
# ==============================================================================
# MIT License
#
# Copyright (c) 2020 Albert Moky
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
    File Content Processor
    ~~~~~~~~~~~~~~~~~~~~~~

"""

from typing import Optional

from dimp import ID, SymmetricKey
from dimp import InstantMessage, SecureMessage, ReliableMessage
from dimp import Envelope
from dimp import ContentType, Content, FileContent

from .processor import ContentProcessor


#
#   File Content Processor
#
class FileContentProcessor(ContentProcessor):

    @property
    def delegate(self):  # MessengerDelegate
        return self.messenger.delegate

    def upload(self, content: FileContent, password: SymmetricKey, msg: InstantMessage):
        data = content.data
        if data is None or len(data) == 0:
            raise ValueError('failed to get file data: %s' % content)
        # encrypt and upload file data onto CDN and save the URL in message content
        encrypted = password.encrypt(data=data)
        if encrypted is None or len(encrypted) == 0:
            raise ValueError('failed to encrypt file data with key: %s' % password)
        url = self.delegate.upload_data(data=encrypted, msg=msg)
        if url is not None:
            # replace 'data' with 'URL'
            content.url = url
            content.data = None
            return True

    def download(self, content: FileContent, password: SymmetricKey, msg: SecureMessage):
        url = content.url
        if url is None or url.find('://') < 0:
            # download URL not found
            return False
        env = msg.envelope
        envelope = Envelope.new(sender=env.sender, receiver=env.receiver, time=env.time)
        envelope.delegate = env.delegate
        if env.group is not None:
            envelope.group = env.group
        if env.type is not None and env.type > 0:
            envelope.type = env.type
        i_msg = InstantMessage.new(content=content, envelope=envelope)
        # download from CDN
        encrypted = self.delegate.download_data(url=url, msg=i_msg)
        if encrypted is None or len(encrypted) == 0:
            content.password = password
            return False
        else:
            # decrypt file data
            data = password.decrypt(data=encrypted)
            if data is None or len(data) == 0:
                raise ValueError('failed to decrypt file data with key: %s' % password)
            content.data = data
            content.url = None
            return True

    #
    #   main
    #
    def process(self, content: Content, sender: ID, msg: ReliableMessage) -> Optional[Content]:
        assert isinstance(content, FileContent), 'file content error: %s' % content
        # TODO: process file content
        return None


# register
ContentProcessor.register(content_type=ContentType.File, processor_class=FileContentProcessor)
ContentProcessor.register(content_type=ContentType.Image, processor_class=FileContentProcessor)
ContentProcessor.register(content_type=ContentType.Audio, processor_class=FileContentProcessor)
ContentProcessor.register(content_type=ContentType.Video, processor_class=FileContentProcessor)
