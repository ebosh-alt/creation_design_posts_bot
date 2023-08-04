import validators
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendMessage, EditMessageText, DeleteMessage, SendPhoto, SendAnimation, SendVideo
from aiogram.types import Message, CallbackQuery, FSInputFile

from bot import keyboards as kb
from bot.const import NewPost, UrlButton, TypeFile
from bot.db import users
from bot.handlers.posts.create_post import get_button
from bot.states import States
from bot.utils.GetMessage import get_mes

router = Router()


def parse_button(data: str) -> tuple[dict, list]:
    # if "|" not in data and "\n" not in data:
    #     new_data = []
    #     if "\n" in data:
    #         data = data.split("\n")
    #     else:
    #         data = data.split(" ")
    #
    #     link = data[-1]
    #     text = " ".join(data[:-1])
    #     button = {}
    #     if validators.url(link) is True:
    #         button.update({text: link})
    #     new_data.append(button)
    # else:
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
    if new_post.url_button is not None:
        keyboard = kb.create_keyboard({"Удалить клавиатуру": "del_button",
                                       "<< Назад": "back_to_create_post"})
    else:
        keyboard = kb.create_keyboard({"<< Назад": "back_to_create_post"})
    await EditMessageText(chat_id=id,
                          message_id=user.message_id,
                          text=get_mes("messages/url_button.md"),
                          reply_markup=keyboard,
                          disable_web_page_preview=True
                          )


@router.callback_query(lambda call: call.data == "back_to_create_post")
async def add_url(call: CallbackQuery, state: FSMContext):
    id = call.from_user.id
    user = users.get(id)
    data = await state.get_data()
    new_post: NewPost = data["post"]
    button = get_button(new_post)
    await state.set_state(States.new_post)
    await state.update_data(post=new_post)
    await EditMessageText(chat_id=id,
                          message_id=user.message_id,
                          text=get_mes("messages/setting_post.md"),
                          reply_markup=kb.create_keyboard(button, 2, 2, 2))


@router.message(States.button)
async def data_button(message: Message, state: FSMContext):
    id = message.from_user.id
    user = users.get(id)
    button_by_post, sizes = parse_button(message.text)
    data = await state.get_data()
    new_post: NewPost = data["post"]
    new_button = UrlButton()
    new_button.button = button_by_post
    new_button.sizes = sizes
    new_post.url_button = new_button
    button_by_mes = get_button(new_post)
    keyboard_by_post = None
    if new_post.hidden_button is not None:
        button_by_post.update({new_post.hidden_button.name: new_post.id_post})
    if button_by_post:
        if new_post.url_button is not None:
            keyboard_by_post = kb.create_keyboard(button_by_post, new_post.url_button.sizes)
        else:
            keyboard_by_post = kb.create_keyboard(button_by_post)
    await DeleteMessage(chat_id=id, message_id=message.message_id)
    # await DeleteMessage(chat_id=id, message_id=new_post.id_post)
    # await DeleteMessage(chat_id=id, message_id=user.message_id)
    if new_post.media.path is None:
        await EditMessageText(chat_id=id,
                              message_id=new_post.id_post,
                              text=new_post.text,
                              reply_markup=keyboard_by_post)
        await EditMessageText(chat_id=id,
                              message_id=user.message_id,
                              text=get_mes("messages/setting_post.md"),
                              reply_markup=kb.create_keyboard(button_by_mes, 2, 2, 2))
    else:
        await DeleteMessage(chat_id=id, message_id=new_post.id_post)
        await DeleteMessage(chat_id=id, message_id=user.message_id)
        file = FSInputFile(new_post.media.path)
        type_file = new_post.media.type
        match type_file:
            case TypeFile.Photo:
                post = await SendPhoto(chat_id=id,
                                       caption=new_post.text,
                                       photo=file,
                                       reply_markup=keyboard_by_post
                                       )
                mes = await SendMessage(chat_id=id,
                                        text=get_mes("messages/setting_post.md"),
                                        reply_markup=kb.create_keyboard(button_by_mes, 2, 2, 2))

            case TypeFile.Video:
                post = await SendVideo(chat_id=id,
                                       caption=new_post.text,
                                       video=file,
                                       reply_markup=keyboard_by_post
                                       )
                mes = await SendMessage(chat_id=id,
                                        text=get_mes("messages/setting_post.md"),
                                        reply_markup=kb.create_keyboard(button_by_mes, 2, 2, 2))
            case _:
                post = await SendMessage(chat_id=id,
                                         text=new_post.text,
                                         reply_markup=keyboard_by_post)
                an = await SendAnimation(chat_id=id,
                                         caption=new_post.text,
                                         animation=file
                                         )
                mes = await SendMessage(chat_id=id,
                                        text=get_mes("messages/setting_post.md"),
                                        reply_markup=kb.create_keyboard(button_by_mes, 2, 2, 2))
                new_post.media.id_sticker = an.message_id

        new_post.id_post = post.message_id

        user.message_id = mes.message_id
    users.update(user)
    await state.set_state(States.new_post)
    await state.update_data(post=new_post)


@router.callback_query(States.button, lambda call: call.data == "del_button")
async def del_buttons(call: CallbackQuery, state: FSMContext):
    id = call.from_user.id
    user = users.get(id)
    data = await state.get_data()
    new_post: NewPost = data["post"]
    new_post.url_button = None
    button_by_mes = get_button(new_post)
    keyboard_by_post = None
    button_by_post = {}
    if new_post.hidden_button is not None:
        button_by_post.update({new_post.hidden_button.name: new_post.id_post})
    if button_by_post:
        if new_post.url_button is not None:
            keyboard_by_post = kb.create_keyboard(button_by_post, new_post.url_button.sizes)
        else:
            keyboard_by_post = kb.create_keyboard(button_by_post)
    if new_post.media.path is None:
        await EditMessageText(chat_id=id,
                              message_id=new_post.id_post,
                              text=new_post.text,
                              reply_markup=keyboard_by_post)
        await EditMessageText(chat_id=id,
                              message_id=user.message_id,
                              text=get_mes("messages/setting_post.md"),
                              reply_markup=kb.create_keyboard(button_by_mes, 2, 2, 2))
    else:
        await DeleteMessage(chat_id=id, message_id=new_post.id_post)
        await DeleteMessage(chat_id=id, message_id=user.message_id)
        file = FSInputFile(new_post.media.path)
        type_file = new_post.media.type
        match type_file:
            case TypeFile.Photo:
                post = await SendPhoto(chat_id=id,
                                       caption=new_post.text,
                                       photo=file,
                                       reply_markup=keyboard_by_post
                                       )
                mes = await SendMessage(chat_id=id,
                                        text=get_mes("messages/setting_post.md"),
                                        reply_markup=kb.create_keyboard(button_by_mes, 2, 2, 2))

            case TypeFile.Video:
                post = await SendVideo(chat_id=id,
                                       caption=new_post.text,
                                       video=file,
                                       reply_markup=keyboard_by_post
                                       )
                mes = await SendMessage(chat_id=id,
                                        text=get_mes("messages/setting_post.md"),
                                        reply_markup=kb.create_keyboard(button_by_mes, 2, 2, 2))
            case _:
                if new_post.media.location:
                    post = await SendMessage(chat_id=id,
                                             text=new_post.text,
                                             reply_markup=keyboard_by_post)
                    an = await SendAnimation(chat_id=id,
                                             caption=new_post.text,
                                             animation=file
                                             )
                    mes = await SendMessage(chat_id=id,
                                            text=get_mes("messages/setting_post.md"),
                                            reply_markup=kb.create_keyboard(button_by_mes, 2, 2, 2))
                else:
                    an = await SendAnimation(chat_id=id,
                                             caption=new_post.text,
                                             animation=file
                                             )
                    post = await SendMessage(chat_id=id,
                                             text=new_post.text,
                                             reply_markup=keyboard_by_post)
                    mes = await SendMessage(chat_id=id,
                                            text=get_mes("messages/setting_post.md"),
                                            reply_markup=kb.create_keyboard(button_by_mes, 2, 2, 2))
                new_post.media.id_sticker = an.message_id

        new_post.id_post = post.message_id

        user.message_id = mes.message_id
    users.update(user)
    await state.set_state(States.new_post)
    await state.update_data(post=new_post)


button_router = router
