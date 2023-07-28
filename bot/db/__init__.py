from .Channels import Channel, Channels
from .Users import User, Users
from .Posts import Post, Posts
from .Buttons import Button, Buttons
from .Url_buttons import UrlButton, UrlButtons
from .Hidden_buttons import HiddenButton, HiddenButtons
from .Media import File, Media

db_file_name = "bot/db/database"
channels = Channels(db_file_name=db_file_name, table_name="channels")
users = Users(db_file_name=db_file_name, table_name="users")
posts = Posts(db_file_name=db_file_name, table_name="users")
buttons = Buttons(db_file_name=db_file_name, table_name="users")
urlButtons = UrlButtons(db_file_name=db_file_name, table_name="users")
hiddenButtons = HiddenButtons(db_file_name=db_file_name, table_name="users")
media = Media(db_file_name=db_file_name, table_name="users")
__all__ = ("channels", "Channel",
           "users", "User",
           "posts", "Post",
           "buttons", "Button",
           "urlButtons", "UrlButton",
           "hiddenButtons", "HiddenButton",
           "media", "File"
           )
