from .add_channel import add_channel
from .setting_channel import setting
from .start import start_router
from .add_editor import new_editor
from .setting_bot import setting_bot_router

routers = (add_channel, setting, start_router, new_editor, setting_bot_router)
