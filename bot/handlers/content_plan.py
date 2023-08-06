from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendMessage, EditMessageText, SendPhoto, SendAnimation, SendVideo, DeleteMessage
from aiogram.types import Message, CallbackQuery, FSInputFile
import datetime
from bot import keyboards as kb
from bot.const import NewPost, TypeFile, HiddenButton
from bot.db import users, posts, postChannels, channels
from bot.handlers.posts.create_post import get_button
from bot.states import States
from bot.utils.GetMessage import get_mes
from bot.utils.send_post import get_info_post

router = Router()


@router.callback_query(lambda call: call.data == "back_to_posts")
@router.message(lambda message: message.text == "Контент план")
async def con_plan(message: Message | CallbackQuery):
    id = message.from_user.id
    user = users.get(id)
    buttons = {}

    for post in posts:
        if post.send_time != 0:
            name_channels = []
            id_channels = postChannels.get_channels(post.id)
            for key in id_channels:
                name_channels.append(channels.get(key).name)
            time = datetime.datetime.fromtimestamp(post.send_time)
            buttons.update({f"{time.strftime('%Y/%m/%d %H:%M:%S')} в {', '.join(name_channels)}": f"{post.id}content"})
    if buttons:
        text = "Все посты которые были запланированы"
    else:
        text = "Постов нет"
    buttons.update({"<< Назад": "back_to_start"})
    if type(message) is Message:
        await DeleteMessage(chat_id=id, message_id=message.message_id)
    await DeleteMessage(chat_id=id, message_id=user.message_id)
    mes = await SendMessage(chat_id=id,
                            text=text,
                            reply_markup=kb.create_keyboard(buttons))
    user.message_id = mes.message_id
    users.update(user)


@router.callback_query(lambda call: "content" in call.data)
async def get_post(call: CallbackQuery):
    id = call.from_user.id
    user = users.get(id)
    id_post = int(call.data.replace("content", ""))
    post = posts.get(id_post)
    data = get_info_post(post)
    time = datetime.datetime.fromtimestamp(post.send_time)
    text = get_mes("messages/info_post.md", id_post=id_post, text=data[0], time=f"{time.strftime('%Y/%m/%d %H:%M:%S')}")
    id_channels = postChannels.get_channels(post.id)
    for key in id_channels:
        channel = channels.get(key)
        text += f"\n[{channel.name}]({channel.link})"
    button = {"Удалить": f"del_{id_post}",
              "<< Назад": "back_to_posts"}
    await EditMessageText(chat_id=id,
                          message_id=user.message_id,
                          text=text,
                          reply_markup=kb.create_keyboard(button, 2))


@router.callback_query(lambda call: "del_" in call.data)
async def del_post(call: CallbackQuery):
    id_post = int(call.data.replace("del_", ""))
    post = posts.get(id_post)
    post.send_time = 0
    posts.update(post)
    await con_plan(call)


content_plan = router
