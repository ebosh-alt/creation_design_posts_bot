from typing import NewType

NewHiddenButton = NewType('NewHiddenButton', str)
NewUrlButton = NewType('NewUrlButton', str)
NewPhoto = NewType('NewPhoto', str)
NewVideo = NewType('NewVideo', str)
NewEmoji = NewType('NewEmoji', str)


class NewButton:
    type: NewHiddenButton | NewUrlButton = None
    button: dict = None


class NewMedia:
    path: str = None
    type: NewVideo | NewPhoto | NewEmoji = None


class NewPost:
    id_channel: int = None
    text: str = None
    url_button: list[NewButton] = None
    hidden_button: list[NewButton] = None
    media: dict[int, NewMedia] = None
    id_post: int = None
