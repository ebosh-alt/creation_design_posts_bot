from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendMessage, GetChatMemberCount, GetChat, DeleteMessage
from aiogram.types import Message

from bot import keyboards as kb

from bot.states import States
from bot.utils.GetMessage import get_mes
from bot.db import Channel, channels, User, users
from bot import keyboards as kb

router = Router()


@router.message(Command("start"))
async def start(message: Message):
    id = message.from_user.id
    if id not in users:
        user = User(id=id)
        users.add(user)
    else:
        user = users.get(id)
    mes = await SendMessage(chat_id=id,
                            text=get_mes("messages/start.md"),
                            reply_markup=kb.start)
    user.message_id = mes.message_id

    users.update(user)


start_router = router
