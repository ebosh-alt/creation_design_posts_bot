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


class NewButton:
    button: dict = None
    sizes: list = None


class NewMedia:
    path: str = None
    type: TypeFile = None
    location: bool = True
    id_sticker: int = None


class NewPost:
    id_channel: int = None
    text: str = None
    url_button: NewButton = None
    hidden_button: list[NewButton] = None
    media: NewMedia = NewMedia
    id_post: int = None
