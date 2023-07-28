from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendMessage, EditMessageText, DeleteMessage
from aiogram.types import Message, CallbackQuery

from bot import keyboards as kb
from bot.const import NewPost

from bot.states import States
from bot.utils.GetMessage import get_mes
from bot.db import Channel, channels, users

router = Router()


@router.message(Command("newpost"))
@router.message(lambda message: message.text == "Создать пост")
async def newpost_start(message: Message, state: FSMContext):
    id = message.from_user.id
    user = users.get(id)
    button = {}
    for channel in channels:
        button.update({channel.name: f"new_post_{channel.id}"})
    keyboard = kb.create_keyboard(button)
    await DeleteMessage(chat_id=id, message_id=user.message_id)
    await DeleteMessage(chat_id=id, message_id=message.message_id)
    mess = await SendMessage(chat_id=id,
                             text=get_mes("messages/start_new_post.md"),
                             reply_markup=keyboard
                             )
    user.message_id = mess.message_id
    users.update(user)


@router.callback_query(lambda call: "new_post_" in call.data or call.data == "change_text")
async def choice_channel(call: CallbackQuery, state: FSMContext):
    id = call.from_user.id
    user = users.get(id)
    if call.data != "change_text":
        id_channel = int(call.data.replace("new_post_", ""))
        new_post = NewPost()
        new_post.id_channel = id_channel
        channel = channels.get(id_channel)
        await state.set_state(States.new_post)
        await state.update_data(post=new_post)
    else:
        data = await state.get_data()

        new_post: NewPost = data["post"]
        channel = channels.get(new_post.id_channel)
        await DeleteMessage(chat_id=id, message_id=call.message.message_id)
    await EditMessageText(chat_id=id,
                          message_id=user.message_id,
                          text=get_mes("messages/text_by_post.md", name=channel.name, link=channel.link),
                          )


@router.message(States.new_post)
async def inp_text(message: Message, state: FSMContext):
    id = message.from_user.id
    user = users.get(id)
    data = await state.get_data()
    new_post: NewPost = data["post"]
    new_post.text = message.text
    new_post.id_post = user.message_id
    await DeleteMessage(chat_id=id, message_id=message.message_id)
    if new_post.media is None and new_post.url_button is None and new_post.hidden_button is None:
        button = {
            "Изменить текст": "change_text",
            "Добавить медиа": "add_media",
            "+ URL-кнопки": "add_url_button",
            "+ Скрытое продолжение": "add_hidden_button",
            "<< Отменить": "cancel",
            "Продолжить >>": "continue",
        }
        await EditMessageText(chat_id=id,
                              message_id=user.message_id,
                              text=new_post.text)

        mes = await SendMessage(chat_id=id,
                                text=get_mes("messages/setting_post.md"),
                                reply_markup=kb.create_keyboard(button, 2, 2, 2))
        user.message_id = mes.message_id
        users.update(user)


new_post_router = router
