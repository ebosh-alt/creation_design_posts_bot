from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.methods import GetChatMemberCount, EditMessageText, DeleteMessage, AnswerCallbackQuery, \
    LeaveChat
from aiogram.types import Message, CallbackQuery
from bot import keyboards as kb

from bot.states import States
from bot.utils.GetMessage import get_mes
from bot.db import channels, users
from bot.handlers.setting.setting_bot import settings
router = Router()


@router.callback_query(States.setting_channel, lambda call: "confirm_public" in call.data or call.data == "back")
@router.callback_query(lambda call: "settings_channel" in call.data)
async def settings_channel(call: CallbackQuery | Message, state: FSMContext):
    id = call.from_user.id
    user = users.get(id)
    if "confirm_public" in call.data:
        data = await state.get_data()
        id_channel = data["id"]
        channel = channels.get(id_channel)
        channel.confirm_public = not channel.confirm_public
    elif "settings_channel_" in call.data:
        id_channel = int(call.data.split('settings_channel_')[1])
        channel = channels.get(id_channel)
        await state.set_state(States.setting_channel)
        await state.update_data(id=id_channel)
    else:
        data = await state.get_data()
        id_channel = data["id"]
        channel = channels.get(id_channel)
    if channel.confirm_public:
        button = {
            # "Автоподпись": "signing",
            "✅Подтверждать публикацию": f"confirm_public",
            "Назад": "back_to_setting",
            "Удалить канал/группу": "delete_channel",
        }
    else:
        button = {
            # "Автоподпись": "signing",
            "❌Подтверждать публикацию": f"confirm_public",
            "Назад": "back_to_setting",
            "Удалить канал/группу": "delete_channel",
        }
    count = await GetChatMemberCount(chat_id=id_channel)
    await EditMessageText(chat_id=id,
                          message_id=user.message_id,
                          text=get_mes("messages/about_channel.md",
                                       name_channel=channel.name,
                                       link_to_channel=channel.link,
                                       count=count),
                          reply_markup=kb.create_keyboard(button, 1, 1, 2))
    channels.update(channel)


@router.callback_query(States.setting_channel, lambda call: call.data == "delete_channel")
async def del_channel(call: CallbackQuery, state: FSMContext):
    user = users.get(call.from_user.id)
    data = await state.get_data()
    id_channel = data["id"]
    del channels[id_channel]
    await AnswerCallbackQuery(callback_query_id=call.id, text="Канал удален", show_alert=True)
    await state.clear()
    await DeleteMessage(chat_id=call.from_user.id, message_id=user.message_id)
    await LeaveChat(chat_id=id_channel)
    await settings(call, state)


@router.callback_query(lambda call: "signing" in call.data)
async def work_signing(call: CallbackQuery, state: FSMContext):
    id = call.from_user.id
    user = users.get(id)
    data = await state.get_data()
    id_channel = data["id"]
    channel = channels.get(id_channel)
    if call.data == "del_signing":
        channel.signing = None
    if channel.signing is None:
        await EditMessageText(chat_id=id,
                              message_id=user.message_id,
                              text=get_mes("messages/signing.md",
                                           name_channel=channel.name,
                                           link_to_channel=channel.link,
                                           ),
                              reply_markup=kb.back)
    else:
        await input_sign_channel(call, state)
    channels.update(channel)


@router.callback_query(lambda call: "empty_string" == call.data)
@router.message(States.setting_channel, lambda message: message.text[0] != "/")
async def input_sign_channel(message: Message | CallbackQuery, state: FSMContext):
    id = message.from_user.id
    user = users.get(id)
    data = await state.get_data()
    id_channel = data["id"]
    channel = channels.get(id_channel)
    if type(message) is CallbackQuery:
        if "empty_string" == message.data:
            channel.empty_string = not channel.empty_string
    else:
        channel.signing = message.text
        await DeleteMessage(chat_id=id,
                            message_id=message.message_id)
    if not channel.empty_string:
        button = {
            "❌Пустая строка перед автоподписью": "empty_string",
            "Удалить автоподпись": "del_signing",
            "Назад": "back",
        }
    else:
        button = {
            "✅Пустая строка перед автоподписью": "empty_string",
            "Удалить автоподпись": "del_signing",
            "Назад": "back",
        }
    await EditMessageText(chat_id=id,
                          message_id=user.message_id,
                          text=get_mes("messages/inp_signing.md",
                                       name_channel=channel.name,
                                       link_to_channel=channel.link,
                                       signing=channel.signing
                                       ),
                          reply_markup=kb.create_keyboard(button))
    channels.update(channel)


setting = router
