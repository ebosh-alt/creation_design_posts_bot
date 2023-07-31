from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.methods import EditMessageText, DeleteMessage, SendPhoto, SendVideo, SendAnimation, SendMessage
from aiogram.types import Message, CallbackQuery, FSInputFile

from bot import keyboards as kb
from bot.config import bot
from bot.const import NewPost, NewMedia, TypeFile
from bot.db import users
from bot.handlers.posts.create_post import get_button
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
        destination = f"bot/media/{message.sticker.file_id}_{message.message_id}.tgs"
        type_file = TypeFile.Sticker
    else:
        file = message.video
        destination = f"bot/media/{message.video.file_id}_{message.message_id}.mp4"
        type_file = TypeFile.Video
    await bot.download(
        file=file,
        destination=destination
    )
    return destination, type_file


def get_button_(new_post: NewPost, data: str = None):
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
    buttons = get_button_(new_post)
    if new_post.media.path is None:
        new_post.media = NewMedia()
        await state.update_data(post=new_post)
        await EditMessageText(chat_id=id,
                              message_id=user.message_id,
                              text=get_mes("messages/add_media.md"),
                              reply_markup=kb.create_keyboard(buttons, 2, 1))
    else:
        button = {}
        if new_post.media.type is TypeFile.Sticker:
            if new_post.media.location:
                button = {"✅Под сообщением": "under",
                          "Над сообщением": "abow", }
            else:
                button = {"Под сообщением": "under",
                          "✅Над сообщением": "abow", }

        button.update(buttons)
        await EditMessageText(chat_id=id,
                              message_id=user.message_id,
                              text=get_mes("messages/add_media.md"),
                              reply_markup=kb.create_keyboard(button, 2, 1, 1)
                              )


@router.message(States.new_post, lambda message: message.photo or message.video or message.sticker)
async def asl(message: Message, state: FSMContext):
    id = message.from_user.id
    user = users.get(id)
    file_path, type_file = await download_media(message)
    data = await state.get_data()
    new_post = data["post"]
    new_post.media.path = file_path
    new_post.media.type = type_file
    await DeleteMessage(chat_id=id, message_id=message.message_id)
    await DeleteMessage(chat_id=id, message_id=new_post.id_post)
    await DeleteMessage(chat_id=id, message_id=user.message_id)
    if new_post.media.type is TypeFile.Sticker:
        await DeleteMessage(chat_id=id, message_id=new_post.media.id_sticker)
    keyboard_by_post = None
    buttons = {}
    if new_post.url_button is not None:
        buttons.update(new_post.url_button.button)
    if new_post.hidden_button is not None:
        buttons.update({new_post.hidden_button.name: new_post.id_post})
    if buttons:
        if new_post.url_button is not None:
            keyboard_by_post = kb.create_keyboard(buttons, new_post.url_button.sizes)
        else:
            keyboard_by_post = kb.create_keyboard(buttons)

    file = FSInputFile(file_path)
    button = get_button(new_post)

    match type_file:
        case TypeFile.Photo:
            post = await SendPhoto(chat_id=id,
                                   caption=new_post.text,
                                   photo=file,
                                   reply_markup=keyboard_by_post
                                   )
            mes = await SendMessage(chat_id=id,
                                    text=get_mes("messages/setting_post.md"),
                                    reply_markup=kb.create_keyboard(button, 2, 2, 2))

        case TypeFile.Video:
            post = await SendVideo(chat_id=id,
                                   caption=new_post.text,
                                   video=file,
                                   reply_markup=keyboard_by_post
                                   )
            mes = await SendMessage(chat_id=id,
                                    text=get_mes("messages/setting_post.md"),
                                    reply_markup=kb.create_keyboard(button, 2, 2, 2))
        case _:
            post = await SendMessage(chat_id=id,
                                     text=new_post.text,
                                     reply_markup=keyboard_by_post)
            an = await SendAnimation(chat_id=id,
                                     caption=new_post.text,
                                     animation=file
                                     )
            new_post.media.id_sticker = an.message_id
            button = {"✅Под сообщением": "under",
                      "Над сообщением": "abow",
                      "Готово": "back_to_create_post"}
            mes = await SendMessage(chat_id=id,
                                    text=get_mes("messages/add_emoji.md"),
                                    reply_markup=kb.create_keyboard(button, 2, 1))

    new_post.id_post = post.message_id
    user.message_id = mes.message_id
    await state.update_data(post=new_post)
    users.update(user)


@router.callback_query(States.new_post, lambda call: call.data in ["under", "abow"])
async def change_location(call: CallbackQuery, state: FSMContext):
    id = call.from_user.id
    user = users.get(id)
    data = await state.get_data()
    new_post = data["post"]

    file = FSInputFile(new_post.media.path)
    keyboard = None
    if new_post.url_button:
        button, sizes = new_post.url_button.button, new_post.url_button.sizes
        keyboard = kb.create_keyboard(button, sizes)
    await DeleteMessage(chat_id=id, message_id=call.message.message_id)
    await DeleteMessage(chat_id=id, message_id=new_post.id_post)
    await DeleteMessage(chat_id=id, message_id=new_post.media.id_sticker)
    if not new_post.media.location and call.data == "under":
        button = {"✅Под сообщением": "under",
                  "Над сообщением": "abow", }
        post = await SendMessage(chat_id=id,
                                 text=new_post.text,
                                 reply_markup=keyboard)
        await SendAnimation(chat_id=id,
                            caption=new_post.text,
                            animation=file)
    elif new_post.media.location and call.data == "abow":
        button = {"Под сообщением": "under",
                  "✅Над сообщением": "abow", }
        an = await SendAnimation(chat_id=id,
                                 caption=new_post.text,
                                 animation=file)
        new_post.media.id_sticker = an.message_id
        post = await SendMessage(chat_id=id,
                                 text=new_post.text,
                                 reply_markup=keyboard)
    else:
        return 404
    button.update({"<< Назад": "back_to_create_post"})
    new_post.media.location = not new_post.media.location
    mes = await SendMessage(chat_id=id,
                            text=get_mes("messages/add_emoji.md"),
                            reply_markup=kb.create_keyboard(button, 2, 1))
    new_post.id_post = post.message_id
    user.message_id = mes.message_id
    await state.update_data(post=new_post)
    users.update(user)


@router.callback_query(States.new_post, lambda call: call.data == "del_media")
async def del_media_post(call: CallbackQuery, state: FSMContext):
    id = call.from_user.id
    user = users.get(id)
    data = await state.get_data()
    new_post = data["post"]
    type_media = new_post.media.type
    if type_media is TypeFile.Sticker:
        await DeleteMessage(chat_id=id, message_id=new_post.media.id_sticker)
    await DeleteMessage(chat_id=id, message_id=new_post.id_post)
    keyboard_by_post = None
    button_by_post = {}
    if new_post.url_button is not None:
        button_by_post.update(new_post.url_button.button)
    if new_post.hidden_button is not None:
        button_by_post.update({new_post.hidden_button.name: new_post.id_post})
    if button_by_post:
        if new_post.url_button is not None:
            keyboard_by_post = kb.create_keyboard(button_by_post, new_post.url_button.sizes)
        else:
            keyboard_by_post = kb.create_keyboard(button_by_post)

    new_post.media = NewMedia()
    button = get_button(new_post)
    await EditMessageText(chat_id=id,
                          message_id=user.message_id,
                          text=new_post.text,
                          reply_markup=keyboard_by_post
                          )
    mes = await SendMessage(chat_id=id,
                            text=get_mes("messages/setting_post.md"),
                            reply_markup=kb.create_keyboard(button, 2, 2, 2))
    new_post.id_post = user.message_id
    user.message_id = mes.message_id
    users.update(user)
    await state.update_data(post=new_post)


add_media_router = router
