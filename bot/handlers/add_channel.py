from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendMessage, GetChatMemberCount, GetChat, DeleteMessage
from aiogram.types import Message

from bot import keyboards as kb
from bot.handlers.settings import settings_channel

from bot.states import States
from bot.utils.GetMessage import get_mes
from bot.db import Channel, channels, users

router = Router()


@router.message(Command("addchannel"))
async def start_add_channel(message: Message, state: FSMContext):
    id = message.from_user.id
    await state.set_state(States.add_channel)
    mes = await SendMessage(chat_id=id, text=get_mes("messages/start_add_channel.md", user_name_bot="tet"))
    await state.update_data(del_message=mes.message_id)


@router.message(States.add_channel)
async def inp_channel(message: Message, state: FSMContext):
    id = message.from_user.id
    user = users.get(id)
    id_channel = message.forward_from_chat.id

    count_user = await GetChatMemberCount(chat_id=id_channel)
    chat = await GetChat(chat_id=id_channel)
    data = await state.get_data()

    await DeleteMessage(chat_id=id, message_id=message.message_id)
    await DeleteMessage(chat_id=id, message_id=data["del_message"])

    mes = await SendMessage(chat_id=id,
                            text=get_mes("messages/successfully_add_channel.md", name_channel=chat.title,
                                         link_to_channel=chat.invite_link),
                            reply_markup=kb.create_keyboard(
                                {"Настройки канала": f"settings_channel_{message.forward_from_chat.id}"}))

    await state.clear()
    await state.set_state(States.setting_channel)
    await state.update_data(id=id_channel)

    user.message_id = mes.message_id

    channel = Channel(id=id_channel, name=chat.title, count_user=count_user, link=chat.invite_link, confirm_public=True,
                      empty_string=False)
    channels.add(channel)
    users.update(user)

    await settings_channel(message, state)


add_channel = router
