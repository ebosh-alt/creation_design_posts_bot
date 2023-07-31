from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.methods import EditMessageText
from aiogram.types import CallbackQuery

from bot import keyboards as kb
from bot.db import users
from bot.states import States
from bot.utils.GetMessage import get_mes
from bot.utils.invoice_link import get_invoice_link

router = Router()


@router.callback_query(States.add_editor, lambda call: call.data == "new_link")
@router.callback_query(lambda call: call.data == "editors")
async def add_editor(call: CallbackQuery, state: FSMContext):
    id = call.from_user.id
    user = users.get(id)
    link = get_invoice_link(25)
    await state.set_state(States.add_editor)
    await EditMessageText(chat_id=id,
                          message_id=user.message_id,
                          text=get_mes("messages/add_editor.md", invoice_link=link),
                          reply_markup=kb.create_keyboard({"Назад": "back_to_setting_from_editor",
                                                           "Новая ссылка": "new_link"
                                                           }, 2))

new_editor = router
