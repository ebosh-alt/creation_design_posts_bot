from typing import NewType
from enum import Enum

NewHiddenButton = NewType('NewHiddenButton', list)
NewUrlButton = NewType('NewUrlButton', str)
NewPhoto = NewType('NewPhoto', str)
NewVideo = NewType('NewVideo', str)
NewEmoji = NewType('NewEmoji', str)


class TypeFile(Enum):
    Photo = 0
    Video = 1
    Sticker = 2


class UrlButton:
    button: dict = None
    sizes: list = None


class HiddenButton:
    name: str = None
    text_by_subscriber: str = None
    text_by_not_subscriber: str = None
    ready: bool = False

class NewMedia:
    path: str = None
    type: TypeFile = None
    location: bool = True
    id_sticker: int = None


class NewPost:
    id_channel: int = None
    text: str = None
    url_button: UrlButton = None
    hidden_button: HiddenButton = None
    media: NewMedia = NewMedia
    id_post: int = None
