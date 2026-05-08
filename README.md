# Decentralized Instant Messaging (Python SDK)

[![License](https://img.shields.io/github/license/dimchat/sdk-py)](https://github.com/dimchat/sdk-py/blob/master/LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/dimchat/sdk-py/pulls)
[![Platform](https://img.shields.io/badge/Platform-Python%203-brightgreen.svg)](https://github.com/dimchat/sdk-py/wiki)
[![Issues](https://img.shields.io/github/issues/dimchat/sdk-py)](https://github.com/dimchat/sdk-py/issues)
[![Repo Size](https://img.shields.io/github/repo-size/dimchat/sdk-py)](https://github.com/dimchat/sdk-py/archive/refs/heads/master.zip)
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
class CustomizedContentProcessor(BaseContentProcessor):
    """
        Customized Content Processing Unit
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        Handle content for application customized
    """

    # def __init__(self, facebook: Facebook, messenger: Messenger):
    #     super().__init__(facebook=facebook, messenger=messenger)

    # Override
    async def process_content(self, content: Content, r_msg: ReliableMessage) -> List[Content]:
        assert isinstance(content, CustomizedContent), 'customized content error: %s' % content
        customized_filter = get_app_filter()
        # get handler for 'app' & 'mod'
        handler = customized_filter.filter_content(content=content, msg=r_msg)
        return await handler.handle_action(content=content, msg=r_msg, messenger=self.messenger)
```

- CustomizedContentHandler

```python
class CustomizedContentHandler(ABC):
    """
        Handler for Customized Content
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    @abstractmethod
    async def handle_action(self, content: CustomizedContent, msg: ReliableMessage,
                            messenger: Messenger) -> List[Content]:
        """
        Do your job

        @param content:   customized content
        @param msg:       network message
        @param messenger: message transceiver
        @return contents
        """
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.handle_action()'
        )


class BaseCustomizedContentHandler(CustomizedContentHandler):
    """
        Default Handler
        ~~~~~~~~~~~~~~~
    """

    # Override
    async def handle_action(self, content: CustomizedContent, msg: ReliableMessage,
                            messenger: Messenger) -> List[Content]:
        # app = content.application
        app = content.get_str(key='app')
        mod = content.module
        act = content.action
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
```

- CustomizedContentFilter

```python
class CustomizedContentFilter(ABC):

    @abstractmethod
    def filter_content(self, content: CustomizedContent, msg: ReliableMessage) -> CustomizedContentHandler:
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.filter_content()'
        )


class AppCustomizedFilter(CustomizedContentFilter):

    def __init__(self):
        super().__init__()
        self.__default_handler = BaseCustomizedContentHandler()
        self.__handlers: Dict[str, CustomizedContentHandler] = {}

    def set_content_handler(self, app: str, mod: str, handler: CustomizedContentHandler):
        key = '%s:%s' % (app, mod)
        self.__handlers[key] = handler

    # protected
    def get_content_handler(self, app: str, mod: str) -> Optional[CustomizedContentHandler]:
        key = '%s:%s' % (app, mod)
        return self.__handlers.get(key)

    # Override
    def filter_content(self, content: CustomizedContent, msg: ReliableMessage) -> CustomizedContentHandler:
        # app = content.application
        app = content.get_str(key='app', default='')
        mod = content.module
        handler = self.get_content_handler(app=app, mod=mod)
        if handler is not None:
            return handler
        # if the application has too many modules, I suggest you to
        # use different handler to do the jobs for each module.
        return self.__default_handler


class CustomizedFilterExtension:

    @property
    def customized_filter(self) -> CustomizedContentFilter:
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.customized_filter getter'
        )

    @customized_filter.setter
    def customized_filter(self, delegate: CustomizedContentFilter):
        raise NotImplementedError(
            f'Not implemented: {type(self).__module__}.{type(self).__name__}.customized_filter setter'
        )


shared_message_extensions.customized_filter = AppCustomizedFilter()


def customized_extensions() -> CustomizedFilterExtension:
    return shared_message_extensions


def get_app_filter() -> AppCustomizedFilter:
    ext = customized_extensions()
    customized_filter = ext.customized_filter
    if not isinstance(customized_filter, AppCustomizedFilter):
        customized_filter = AppCustomizedFilter()
        ext.customized_filter = customized_filter
    return customized_filter
```

- Example for group querying

```python
class GroupHistoryHandler(BaseCustomizedContentHandler):
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
    async def handle_action(self, content: CustomizedContent, msg: ReliableMessage,
                            messenger: Messenger) -> List[Content]:
        if content.group is None:
            text = 'Group command error.'
            return self._respond_receipt(text=text, envelope=msg.envelope, content=content)
        act = content.action
        if act == GroupHistory.ACT_QUERY:
            # assert GroupHistory.APP == content.application
            assert GroupHistory.MOD == content.module
            return await self.__transform_query_command(content=content, msg=msg, messenger=messenger)
        else:
            # assert False, 'unknown action: %s, %s, sender: %s' % (act, content, sender)
            return await super().handle_action(content=content, msg=msg, messenger=messenger)

    async def __transform_query_command(self, content: CustomizedContent, msg: ReliableMessage,
                                        messenger: Messenger) -> List[Content]:
        info = content.copy_dict()
        info['type'] = ContentType.COMMAND
        info['command'] = QueryCommand.QUERY
        query = Content.parse(content=info)
        if isinstance(query, QueryCommand):
            return await messenger.process_content(content=query, r_msg=msg)
        # else:
        #     assert False, 'query command error: %s, %s, sender: %s' % (query, content, sender)
        text = 'Query command error.'
        return self._respond_receipt(text=text, envelope=msg.envelope, content=content)


# def register_customized_handlers():
#     app_filter = get_app_filter()
#     # 'chat.dim.group:history'
#     app_filter.set_content_handler(app=GroupHistory.APP,
#                                    mod=GroupHistory.MOD,
#                                    handler=GroupHistoryHandler()
#                                    )
```

### ContentProcessorCreator

```python
from typing import Optional

from dimsdk import *

from .handshake import *
from .customized import *


class ClientContentProcessorCreator(BaseContentProcessorCreator):

    # Override
    def create_content_processor(self, msg_type: str) -> Optional[ContentProcessor]:
        # application customized
        if msg_type == ContentType.APPLICATION:
            return CustomizedContentProcessor(facebook=self.facebook, messenger=self.messenger)
        elif msg_type == ContentType.CUSTOMIZED:
            return CustomizedContentProcessor(facebook=self.facebook, messenger=self.messenger)
        
        # ...
        
        # others
        return super().create_content_processor(msg_type=msg_type)

    # Override
    def create_command_processor(self, msg_type: str, cmd: str) -> Optional[ContentProcessor]:
        # handshake
        if cmd == HandshakeCommand.HANDSHAKE:
            return HandshakeCommandProcessor(facebook=self.facebook, messenger=self.messenger)
        
        # ...
        
        # others
        return super().create_command_processor(msg_type=msg_type, cmd=cmd)
```

## Usage

To let your **CustomizedContentProcessor** start to work,
you must override ```BaseContentProcessorCreator``` for message types:

1. ContentType.APPLICATION 
2. ContentType.CUSTOMIZED

and then set your **creator** for ```GeneralContentProcessorFactory``` in the ```MessageProcessor```.

----

Copyright &copy; 2018-2026 Albert Moky
[![Followers](https://img.shields.io/github/followers/moky)](https://github.com/moky?tab=followers)
