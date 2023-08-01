from .Channels import Channel, Channels
from .Users import User, Users
from .Posts import Post, Posts
from .Buttons import Button, Buttons
from .Url_buttons import UrlButton, UrlButtons
from .Hidden_buttons import HiddenButton, HiddenButtons
from .Media import File, Media
from .PostChannel import PostChannel, PostChannels

db_file_name = "D:/telegram_bots/creation_design_posts/bot/db/database"
# db_file_name = "bot/db/database"
channels = Channels(db_file_name=db_file_name, table_name="channels")
users = Users(db_file_name=db_file_name, table_name="users")
posts = Posts(db_file_name=db_file_name, table_name="posts")
urlButtons = UrlButtons(db_file_name=db_file_name, table_name="url_buttons")
hiddenButtons = HiddenButtons(db_file_name=db_file_name, table_name="hidden_buttons")
media = Media(db_file_name=db_file_name, table_name="media")
postChannels = PostChannels(db_file_name=db_file_name, table_name="post_channel")
__all__ = ("channels", "Channel", "Channels",
           "users", "User",
           "posts", "Post", "Posts",
           "urlButtons", "UrlButton",
           "hiddenButtons", "HiddenButton",
           "media", "File",
           "postChannels", "PostChannel"
           )

if __name__ == '__main__':
    data = postChannels.get_channels(id=0)
    print(data)