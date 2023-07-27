from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendMessage, GetChatMemberCount, GetChat, DeleteMessage
from aiogram.types import Message, ChatInviteLink

from bot import keyboards as kb
from bot.config import main_user, link_bot, bot, user_name_bot

from bot.states import States
from bot.utils.GetMessage import get_mes
from bot.db import Channel, channels, User, users
from bot import keyboards as kb
from bot.utils.invoice_link import get_links

router = Router()


@router.message(Command("start"))
async def start(message: Message):
    id = message.from_user.id
    print(message.text)
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
        mes = await SendMessage(chat_id=id,
                                text=get_mes("messages/start.md"),
                                reply_markup=kb.start)
        user.message_id = mes.message_id

        users.update(user)


# @router.message()
# async def test(message: Message):
#
#     await SendMessage(chat_id=message.from_user.id,
#                       text="s",
#                       reply_markup=kb.create_keyboard({"s": f"https://t.me/web_app_search_merletplace_bot?startgroup="}))



start_router = router
