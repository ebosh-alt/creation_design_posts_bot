from .Channels import Channel, Channels
from .Users import User, Users


db_file_name = "bot/db/database"
channels = Channels(db_file_name=db_file_name, table_name="channels")
users = Users(db_file_name=db_file_name, table_name="users")
__all__ = ("channels", "Channel", "users", "User")
