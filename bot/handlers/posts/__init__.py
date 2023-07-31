from .create_post import new_post_router
from .add_url_button import button_router
from .add_media import add_media_router
from .add_hidden_button import add_hidden_router
from .setting_post import setting_post_router

posts_router = (new_post_router, button_router, add_media_router, add_hidden_router, setting_post_router)
