from .create_post import new_post_router
from .add_button import button_router

posts_router = (new_post_router, button_router)
