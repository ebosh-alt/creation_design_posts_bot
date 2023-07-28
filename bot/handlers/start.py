from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendMessage, GetChatMemberCount, GetChat, DeleteMessage
from aiogram.types import Message, ChatInviteLink, CallbackQuery

from bot import keyboards as kb
from bot.config import main_user, link_bot, bot, user_name_bot

from bot.states import States
from bot.utils.GetMessage import get_mes
from bot.db import Channel, channels, User, users
from bot import keyboards as kb
from bot.utils.invoice_link import get_links

router = Router()


@router.callback_query(lambda call: call.data == "cancel")
@router.message(Command("start"))
async def start(message: Message | CallbackQuery):
    id = message.from_user.id
    if type(message) is not CallbackQuery:
        text = message.text.split(" ")
        if id in main_user and id not in users:
            user = User(id=id)
            users.add(user)
        if len(text) == 2:
            invoice_link = f"{link_bot}?start={text[1]}"
            links = get_links()
            if invoice_link in links:
                user = User(id=id)
                users.add(user)
    if id in users:
        user = users.get(id)
        if type(message) is CallbackQuery:
            await DeleteMessage(chat_id=id, message_id=user.message_id)
            await DeleteMessage(chat_id=id, message_id=message.message.message_id)
        mes = await SendMessage(chat_id=id,
                                text=get_mes("messages/start.md"),
                                reply_markup=kb.start)
        user.message_id = mes.message_id

        users.update(user)


start_router = router
