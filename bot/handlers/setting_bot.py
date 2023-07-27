from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendMessage, GetChatMemberCount, EditMessageText, DeleteMessage, AnswerCallbackQuery, \
    LeaveChat
from aiogram.types import Message, CallbackQuery
from bot import keyboards as kb

from bot.states import States
from bot.utils.GetMessage import get_mes
from bot.db import channels, users

router = Router()


@router.callback_query(lambda call: call.data == "back_to_setting")
@router.message(lambda message: message.text == "Настройки")
async def settings(message: Message | CallbackQuery, state: FSMContext):
    id = message.from_user.id
    user = users.get(id)

    button = {
        "Редакторы": "editors",
        "Добавить канал": "add_channel",
        "Добавить группу": "add_group",
    }

    for channel in channels:
        button.update({channel.name: f"settings_channel_{channel.id}"})
    if type(message) is CallbackQuery:
        if message.data == "back_to_setting":
            await state.clear()
    else:
        print(type(id), type(user.message_id), type(message.message_id))
        await DeleteMessage(chat_id=id, message_id=user.message_id)
        await DeleteMessage(chat_id=id, message_id=message.message_id)
    mes = await SendMessage(chat_id=id,
                            text=get_mes("messages/settings.md"),
                            reply_markup=kb.create_keyboard(button, 1, 2))
    user.message_id = mes.message_id
    users.update(user)


setting_bot_router = router
