from bot.handlers.setting.add_channel import add_channel
from bot.handlers.setting.setting_channel import setting
from bot.handlers.setting.add_editor import new_editor
from bot.handlers.setting.setting_bot import setting_bot_router
from bot.handlers.setting.add_group import group_add

setting_routers = (add_channel, setting, new_editor, setting_bot_router, group_add)
