import validators
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendMessage, EditMessageText, DeleteMessage
from aiogram.types import Message, CallbackQuery

from bot import keyboards as kb
from bot.const import NewPost, NewButton, NewUrlButton
from bot.db import users
from bot.states import States
from bot.utils.GetMessage import get_mes

router = Router()


def parse_button(data: str) -> tuple[dict, list]:
    if "|" not in data:
        new_data = []
        if "\n" in data:
            data = data.split("\n")
        else:
            data = data.split(" ")
        print(data)
        link = data[-1]
        text = " ".join(data[:-1])
        button = {}
        if validators.url(link) is True:
            button.update({text: link})
        new_data.append(button)
    else:
        data = data.split("\n")
        new_data = []
        button = {}
        for i in range(len(data)):
            line = data[i]
            line = line.strip().split("|")

            for butt in line:
                butt = butt.strip().split(" ")

                link = butt[-1]
                text = " ".join(butt[:-1])
                if validators.url(link) is True:
                    button.update({text: link})

            new_data.append(button)
            button = {}
    buttons = {}
    sizes = []
    for i in new_data:
        sizes.append(len(i))
        buttons.update(i)
    return buttons, sizes


@router.callback_query(lambda call: call.data == "add_url_button")
async def add_url(call: CallbackQuery, state: FSMContext):
    id = call.from_user.id
    user = users.get(id)
    data = await state.get_data()
    await state.set_state(States.button)
    new_post: NewPost = data["post"]
    await state.update_data(post=new_post)
    await EditMessageText(chat_id=id,
                          message_id=user.message_id,
                          text=get_mes("messages/url_button.md"),
                          disable_web_page_preview=True
                          )


@router.message(States.button)
async def data_button(message: Message, state: FSMContext):
    id = message.from_user.id
    user = users.get(id)
    buttons, sizes = parse_button(message.text)
    data = await state.get_data()
    new_post: NewPost = data["post"]
    new_button = NewButton()
    new_button.button = buttons
    new_button.sizes = sizes
    new_post.url_button = new_button

    button = {
        "Изменить текст": "change_text",
        "Добавить медиа": "add_media",
        "Изменить URL-кнопки": "add_url_button",
        "+ Скрытое продолжение": "add_hidden_button",
        "<< Отменить": "cancel",
        "Продолжить >>": "continue",
    }
    await DeleteMessage(chat_id=id, message_id=message.message_id)
    await DeleteMessage(chat_id=id, message_id=new_post.id_post)
    await DeleteMessage(chat_id=id, message_id=user.message_id)
    print(buttons)
    post = await SendMessage(chat_id=message.from_user.id,
                             message_id=new_post.id_post,
                             text=new_post.text,
                             reply_markup=kb.create_keyboard(buttons, sizes))
    mes = await SendMessage(chat_id=id,
                            message_id=user.message_id,
                            text=get_mes("messages/setting_post.md"),
                            reply_markup=kb.create_keyboard(button, 2, 2, 2))
    new_post.id_post = post.message_id

    user.message_id = mes.message_id
    users.update(user)
    await state.set_state(States.new_post)
    await state.update_data(post=new_post)


button_router = router
