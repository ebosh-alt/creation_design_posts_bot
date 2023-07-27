from aiogram import Router
from aiogram.methods import GetChatMemberCount, EditMessageText
from aiogram.types import Message, CallbackQuery

from bot import keyboards as kb
from bot.config import user_name_bot
from bot.utils.GetMessage import get_mes
from bot.db import channels, users, Channel

router = Router()


@router.callback_query(lambda call: call.data == "add_group")
async def add_group(call: CallbackQuery):
    id = call.from_user.id
    user = users.get(id)
    await EditMessageText(chat_id=id,
                          message_id=user.message_id,
                          text=get_mes("messages/add_group.md"),
                          reply_markup=kb.create_keyboard(
                              {"Выбрать группу": f"https://t.me/{user_name_bot.replace('@', '')}?startgroup="})
                          )


@router.my_chat_member()
async def new_chat_members(message: Message):
    try:
        id = message.from_user.id
        user = users.get(id)
        id_group = message.chat.id
        title = message.chat.title
        count_user = await GetChatMemberCount(chat_id=id_group)
        link = f"https://t.me/c/{str(id_group).replace('-100', '')}"
        channel = Channel(id=id_group, name=title, count_user=count_user, link=link,
                          confirm_public=True,
                          empty_string=False)
        channels.add(channel)
        await EditMessageText(chat_id=id,
                              message_id=user.message_id,
                              text=get_mes("messages/successfully_add_group.md", name_group=title, link_group=link),
                              reply_markup=kb.create_keyboard(
                                  {"Настройки группы": f"settings_channel_{id_group}"}))
    except Exception as e:
        print(e)
        pass


group_add = router
