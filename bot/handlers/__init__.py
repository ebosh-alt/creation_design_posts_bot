from bot.handlers.setting import setting_routers
from bot.handlers.posts import posts_router
from .start import start_router

routers = (*setting_routers, *posts_router, start_router)
