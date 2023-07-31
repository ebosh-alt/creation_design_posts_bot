from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendMessage, EditMessageText, SendPhoto, SendAnimation, SendVideo, DeleteMessage
from aiogram.types import Message, CallbackQuery, FSInputFile

from bot import keyboards as kb
from bot.const import NewPost, TypeFile, HiddenButton
from bot.db import users
from bot.handlers.posts.create_post import get_button
from bot.states import States
from bot.utils.GetMessage import get_mes

router = Router()


@router.callback_query(lambda call: call.data == "add_hidden_button")
async def add_hid(call: CallbackQuery, state: FSMContext):
    id = call.from_user.id
    user = users.get(id)
    data = await state.get_data()
    await state.set_state(States.hidden_button)
    new_post: NewPost = data["post"]
    if new_post.hidden_button is None:
        new_post.hidden_button = HiddenButton()
        keyboard = kb.create_keyboard({"<< Назад": "back_to_create_post"})
    else:
        keyboard = kb.create_keyboard({"Удалить клавиатуру": "del_button",
                                       "<< Назад": "back_to_create_post"})
    await state.update_data(post=new_post)
    await EditMessageText(chat_id=id,
                          message_id=user.message_id,
                          text="Введите название для кнопки",
                          reply_markup=keyboard,
                          disable_web_page_preview=True
                          )


@router.message(States.hidden_button)
async def inp_data_hid_but(message: Message, state: FSMContext):
    id = message.from_user.id
    user = users.get(id)
    data = await state.get_data()
    new_post: NewPost = data["post"]
    await DeleteMessage(chat_id=id, message_id=message.message_id)
    if new_post.hidden_button.ready:
        new_post.hidden_button = HiddenButton()

    if new_post.hidden_button.name is None:
        new_post.hidden_button.name = message.text
        text = "Введите текст для подписчиков"
    elif new_post.hidden_button.text_by_subscriber is None:
        new_post.hidden_button.text_by_subscriber = message.text
        text = "Введите текст для тех кто не подписан"
    else:
        new_post.hidden_button.text_by_not_subscriber = message.text
        new_post.hidden_button.ready = True
        button = get_button(new_post)

        keyboard_by_post = None
        button_by_post = {}
        if new_post.url_button is not None:
            button_by_post.update(new_post.url_button.button)
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
                                  reply_markup=kb.create_keyboard(button, 2, 2, 2))
        else:
            await DeleteMessage(chat_id=id, message_id=user.message_id)
            await DeleteMessage(chat_id=id, message_id=new_post.id_post)
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
                                            reply_markup=kb.create_keyboard(button, 2, 2, 2))

                case TypeFile.Video:
                    post = await SendVideo(chat_id=id,
                                           caption=new_post.text,
                                           video=file,
                                           reply_markup=keyboard_by_post
                                           )
                    mes = await SendMessage(chat_id=id,
                                            text=get_mes("messages/setting_post.md"),
                                            reply_markup=kb.create_keyboard(button, 2, 2, 2))
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
                                            reply_markup=kb.create_keyboard(button, 2, 2, 2))
                    new_post.media.id_sticker = an.message_id
            new_post.id_post = post.message_id
            user.message_id = mes.message_id
            users.update(user)
        await state.set_state(States.new_post)
        await state.update_data(post=new_post)


        return 200
    await state.update_data(post=new_post)
    await EditMessageText(chat_id=id,
                          message_id=user.message_id,
                          text=text)


@router.callback_query(States.hidden_button, lambda call: call.data == "del_button")
async def del_buttons(call: CallbackQuery, state: FSMContext):
    id = call.from_user.id
    user = users.get(id)
    data = await state.get_data()
    new_post: NewPost = data["post"]
    new_post.hidden_button = None
    button_by_mes = get_button(new_post)
    keyboard_by_post = None
    button_by_post = {}
    if new_post.url_button is not None:
        button_by_post.update(new_post.url_button.button)
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


add_hidden_router = router
