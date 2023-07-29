import requests
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.methods import EditMessageText, DeleteMessage, GetFile, SendPhoto, SendMessage
from aiogram.types import Message, CallbackQuery, FSInputFile

from bot import keyboards as kb
from bot.config import api_key, bot
from bot.const import NewPost, NewMedia, TypeFile
from bot.db import users
from bot.states import States
from bot.utils.GetMessage import get_mes

router = Router()


async def download_media(message) -> tuple:
    if message.photo:
        file = message.photo[-1]
        destination = f"bot/media/{message.photo[-1].file_id}_{message.message_id}.jpg"
        type_file = TypeFile.Photo
    elif message.sticker:
        file = message.sticker
        destination = f"bot/media/{message.photo[-1].file_id}_{message.message_id}.webp"
        type_file = TypeFile.Sticker
    else:
        file = message.video
        destination = f"bot/media/{message.photo[-1].file_id}_{message.message_id}.mp4"
        type_file = TypeFile.Video
    await bot.download(
        file=file,
        destination=destination
    )
    return destination, type_file


def get_button(new_post: NewPost, data: str = None):
    button = {}

    if data == "under_text" and new_post.media.location is True or data is None and new_post.media.location is False:
        if new_post.media.path is None:
            button = {
                # "✅Под текстом": "under_text",
                # "Над текстом": "abow_text",
                "<< Назад": "back_to_create_post",
            }
        else:
            button = {
                # "✅Под текстом": "under_text",
                # "Над текстом": "abow_text",
                "Удалить медиа": "del_media",
                "<< Назад": "back_to_create_post",
            }
    elif data == "abow_text" and new_post.media.location is False or data is None and new_post.media.location is True:
        if new_post.media.path is None:
            button = {
                # "Под текстом": "under_text",
                # "✅Над текстом": "abow_text",
                "<< Назад": "back_to_create_post",
            }
        else:
            button = {
                # "Под текстом": "under_text",
                # "✅Над текстом": "abow_text",
                "Удалить медиа": "del_media",
                "<< Назад": "back_to_create_post",
            }
    return button


@router.callback_query(States.new_post, lambda call: call.data == "add_media")
async def start_add_media(call: CallbackQuery, state: FSMContext):
    id = call.from_user.id
    user = users.get(id)
    data = await state.get_data()
    new_post: NewPost = data["post"]
    button = get_button(new_post)
    if new_post.media.path is not None:
        new_post.media = NewMedia()
        await state.update_data(post=new_post)
    await EditMessageText(chat_id=id,
                          message_id=user.message_id,
                          text=get_mes("messages/add_media.md"),
                          reply_markup=kb.create_keyboard(button, 2, 1))


@router.callback_query(States.new_post, lambda call: call.data in ["under_text", "abow_text"])
async def change_location_text(call: CallbackQuery, state: FSMContext):
    id = call.from_user.id
    user = users.get(id)
    data = await state.get_data()
    new_post: NewPost = data["post"]
    button = get_button(new_post, call.data)
    if button:
        new_post.media.location = not new_post.media.location
        await state.update_data(post=new_post)
        if new_post.media.path is None:
            button.update({"<< Назад": "back_to_create_post"})
            await EditMessageText(chat_id=id,
                                  message_id=user.message_id,
                                  text=get_mes("messages/add_media.md"),
                                  reply_markup=kb.create_keyboard(button, 2, 1)
                                  )
        else:
            button.update({"Удалить медиа": "del_media", "<< Назад": "back_to_create_post"})


@router.message(lambda message: message.photo or message.video or message.sticker)
async def asl(message: Message, state: FSMContext):
    id = message.from_user.id
    user = users.get(id)
    file_path, type_file = await download_media(message)
    data = await state.get_data()
    new_post = data["post"]
    new_post.media.path = file_path
    new_post.media.type = type_file
    await state.update_data(post=new_post)
    await DeleteMessage(chat_id=id, message_id=message.message_id)
    await DeleteMessage(chat_id=id, message_id=new_post.id_post)
    await DeleteMessage(chat_id=id, message_id=user.message_id)
    if type_file is TypeFile.Photo:
        keyboard = None
        if new_post.url_button:
            button, sizes = new_post.url_button.button, new_post.url_button.sizes
            keyboard = kb.create_keyboard(button, sizes)
        photo = FSInputFile(file_path)
        await SendPhoto(chat_id=id,
                        caption=new_post.text,
                        photo=photo,
                        reply_markup=keyboard
                        )


add_media_router = router
