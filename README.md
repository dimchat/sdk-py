# Decentralized Instant Messaging (Python SDK)

[![License](https://img.shields.io/github/license/dimchat/sdk-py)](https://github.com/dimchat/sdk-py/blob/master/LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/dimchat/sdk-py/pulls)
[![Platform](https://img.shields.io/badge/Platform-Python%203-brightgreen.svg)](https://github.com/dimchat/sdk-py/wiki)
[![Issues](https://img.shields.io/github/issues/dimchat/sdk-py)](https://github.com/dimchat/sdk-py/issues)
[![Repo Size](https://img.shields.io/github/repo-size/dimchat/sdk-py)](https://github.com/dimchat/sdk-py/archive/refs/heads/main.zip)
[![Tags](https://img.shields.io/github/tag/dimchat/sdk-py)](https://github.com/dimchat/sdk-py/tags)
[![Version](https://img.shields.io/pypi/v/dimsdk)](https://pypi.org/project/dimsdk)

[![Watchers](https://img.shields.io/github/watchers/dimchat/sdk-py)](https://github.com/dimchat/sdk-py/watchers)
[![Forks](https://img.shields.io/github/forks/dimchat/sdk-py)](https://github.com/dimchat/sdk-py/forks)
[![Stars](https://img.shields.io/github/stars/dimchat/sdk-py)](https://github.com/dimchat/sdk-py/stargazers)
[![Followers](https://img.shields.io/github/followers/dimchat)](https://github.com/orgs/dimchat/followers)

## Dependencies

* Latest Versions

| Name | Version | Description |
|------|---------|-------------|
| [Ming Ke Ming (名可名)](https://github.com/dimchat/mkm-py) | [![Version](https://img.shields.io/pypi/v/mkm)](https://pypi.org/project/mkm) | Decentralized User Identity Authentication |
| [Dao Ke Dao (道可道)](https://github.com/dimchat/dkd-py) | [![Version](https://img.shields.io/pypi/v/dkd)](https://pypi.org/project/dkd) | Universal Message Module |
| [DIMP (去中心化通讯协议)](https://github.com/dimchat/core-py) | [![Version](https://img.shields.io/pypi/v/dimp)](https://pypi.org/project/dimp) | Decentralized Instant Messaging Protocol |

## Extensions

### Content

extends [CustomizedContent](https://github.com/dimchat/core-py#extends-content)

### ContentProcessor

```python
from typing import Optional, List, Dict

from dimsdk import *
from dimsdk.cpu import *


class AppCustomizedProcessor(CustomizedContentProcessor):
    """
        Customized Content Processing Unit
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        Handle content for application customized
    """

    def __init__(self, facebook: Facebook, messenger: Messenger):
        super().__init__(facebook=facebook, messenger=messenger)
        self.__handlers: Dict[str, CustomizedContentHandler] = {}

    def set_handler(self, app: str, mod: str, handler: CustomizedContentHandler):
        key = '%s:%s' % (app, mod)
        self.__handlers[key] = handler

    # protected
    def get_handler(self, app: str, mod: str) -> Optional[CustomizedContentHandler]:
        key = '%s:%s' % (app, mod)
        return self.__handlers.get(key)

    # noinspection PyUnusedLocal
    def _filter(self, app: str, mod: str, content: CustomizedContent, msg: ReliableMessage) -> CustomizedContentHandler:
        """ Override for your handler """
        handler = self.get_handler(app=app, mod=mod)
        if handler is not None:
            return handler
        # default handler
        return super()._filter(app=app, mod=mod, content=content, msg=msg)
```

```python
from typing import Optional, List, Dict

from dimsdk import *
from dimsdk.cpu import *

from ...common import GroupHistory


class GroupHistoryHandler(BaseCustomizedHandler):
    """ Command Transform:

        +===============================+===============================+
        |      Customized Content       |      Group Query Command      |
        +-------------------------------+-------------------------------+
        |   "type" : i2s(0xCC)          |   "type" : i2s(0x88)          |
        |   "sn"   : 123                |   "sn"   : 123                |
        |   "time" : 123.456            |   "time" : 123.456            |
        |   "app"  : "chat.dim.group"   |                               |
        |   "mod"  : "history"          |                               |
        |   "act"  : "query"            |                               |
        |                               |   "command"   : "query"       |
        |   "group"     : "{GROUP_ID}"  |   "group"     : "{GROUP_ID}"  |
        |   "last_time" : 0             |   "last_time" : 0             |
        +===============================+===============================+
    """

    # Override
    async def handle_action(self, act: str, sender: ID, content: CustomizedContent,
                            msg: ReliableMessage) -> List[Content]:
        if content.group is None:
            text = 'Group command error.'
            return self._respond_receipt(text=text, envelope=msg.envelope, content=content)
        elif GroupHistory.ACT_QUERY == act:
            assert GroupHistory.APP == content.application
            assert GroupHistory.MOD == content.module
            return await self.__transform_query_command(content=content, msg=msg)
        else:
            # assert False, 'unknown action: %s, %s, sender: %s' % (act, content, sender)
            return await super().handle_action(act=act, sender=sender, content=content, msg=msg)

    async def __transform_query_command(self, content: CustomizedContent, msg: ReliableMessage) -> List[Content]:
        messenger = self.messenger
        if messenger is None:
            assert False, 'messenger lost'
            # return []
        info = content.copy_dictionary()
        info['type'] = ContentType.COMMAND
        info['command'] = GroupCommand.QUERY
        query = Content.parse(content=info)
        if isinstance(query, QueryCommand):
            return await messenger.process_content(content=query, r_msg=msg)
        # else:
        #     assert False, 'query command error: %s, %s, sender: %s' % (query, content, sender)
        text = 'Query command error.'
        return self._respond_receipt(text=text, envelope=msg.envelope, content=content)
```

### ContentProcessorCreator

```python
from typing import Optional

from dimsdk import *
from dimsdk.cpu import *

from .handshake import *
from .customized import *


class ClientContentProcessorCreator(BaseContentProcessorCreator):

    # noinspection PyMethodMayBeStatic
    def _create_customized_content_processor(self, facebook: Facebook, messenger: Messenger) -> AppCustomizedProcessor:
        cpu = AppCustomizedProcessor(facebook=facebook, messenger=messenger)
        # 'chat.dim.group:history'
        handler = GroupHistoryHandler(facebook=facebook, messenger=messenger)
        cpu.set_handler(app=GroupHistory.APP, mod=GroupHistory.MOD, handler=handler)
        return cpu

    # Override
    def create_content_processor(self, msg_type: str) -> Optional[ContentProcessor]:
        # application customized
        if msg_type == ContentType.APPLICATION or msg_type == 'application':
            return self._create_customized_content_processor(facebook=self.facebook, messenger=self.messenger)
        if msg_type == ContentType.CUSTOMIZED or msg_type == 'customized':
            return self._create_customized_content_processor(facebook=self.facebook, messenger=self.messenger)
        # others
        return super().create_content_processor(msg_type=msg_type)

    # Override
    def create_command_processor(self, msg_type: str, cmd: str) -> Optional[ContentProcessor]:
        # handshake
        if cmd == HandshakeCommand.HANDSHAKE:
            return HandshakeCommandProcessor(facebook=self.facebook, messenger=self.messenger)
        # others
        return super().create_command_processor(msg_type=msg_type, cmd=cmd)
```

### ExtensionLoader

```python
from dimsdk import ContentType
from dimsdk.plugins import ExtensionLoader

from ..protocol import HandshakeCommand, BaseHandshakeCommand
from ..protocol import AppCustomizedContent


class CommonExtensionLoader(ExtensionLoader):

    # Override
    def _register_customized_factories(self):
        # Application Customized
        self._set_content_factory(msg_type=ContentType.APPLICATION, content_class=AppCustomizedContent)
        self._set_content_factory(msg_type=ContentType.CUSTOMIZED, content_class=AppCustomizedContent)

    # Override
    def _register_command_factories(self):
        super()._register_command_factories()
        # Handshake
        self._set_command_factory(cmd=HandshakeCommand.HANDSHAKE, command_class=BaseHandshakeCommand)
```

## Usages

You must load all extensions before your business run:

```python
from dimsdk.plugins import ExtensionLoader
from dimplugins import PluginLoader

from .common_loader import CommonExtensionLoader


class LibraryLoader:

    def __init__(self, extensions: ExtensionLoader = None, plugins: PluginLoader = None):
        super().__init__()
        self.__extensions = CommonExtensionLoader() if extensions is None else extensions
        self.__plugins = PluginLoader() if plugins is None else plugins

    def run(self):
        self.__extensions.run()
        self.__plugins.run()


if __name__ == '__main__':
  loader = LibraryLoader()
  loader.run()
  # do your jobs after all extensions loaded.
```

To let your **CustomizedContentProcessor** start to work,
you must override ```BaseContentProcessorCreator``` for message types:

1. ContentType.APPLICATION 
2. ContentType.CUSTOMIZED

and then set your **creator** for ```GeneralContentProcessorFactory``` in the ```MessageProcessor```.

----

Copyright &copy; 2018-2025 Albert Moky
[![Followers](https://img.shields.io/github/followers/moky)](https://github.com/moky?tab=followers)
