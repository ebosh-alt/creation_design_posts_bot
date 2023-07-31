from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendMessage, EditMessageText, SendPhoto, SendAnimation, SendVideo, DeleteMessage, \
    AnswerCallbackQuery
from aiogram.types import Message, CallbackQuery, FSInputFile

from bot import keyboards as kb
from bot.const import NewPost, TypeFile, HiddenButton
from bot.db import users, channels, Channels
from bot.states import States
from bot.utils.GetMessage import get_mes

router = Router()


def check_int(ch: str) -> bool:
    return ch.isdigit()


def get_kb_duration(new_post: NewPost):
    button = {}

    if new_post.duration == 3:
        button.update({"✅3 часа": "duration_3"})
    else:
        button.update({"3 часа": "duration_3"})

    if new_post.duration == 72:
        button.update({"✅72 часа": "duration_72"})
    else:
        button.update({"72 часа": "duration_72"})

    if new_post.duration == 168:
        button.update({"✅7 дней": "duration_168"})
    else:
        button.update({"7 дней": "duration_168"})

    if new_post.duration == 336:
        button.update({"✅14 дней": "duration_336"})
    else:
        button.update({"14 дней": "duration_336"})

    if new_post.duration == 0:
        button.update({"✅Всегда": "duration_0"})
    else:
        button.update({"Всегда": "duration_0"})

    button.update({"<< Назад": "repeat", "Применить": "continue"})
    keyboard = kb.create_keyboard(button, 2, 2, 1, 2)
    return keyboard


def get_kb_time(new_post: NewPost):
    button = {}
    if new_post.time == 1:
        button.update({"✅1 час": 1})
    else:
        button.update({"1 час": 1})

    if new_post.time == 2:
        button.update({"✅1 часа": 2})
    else:
        button.update({"2 часа": 2})

    if new_post.time == 3:
        button.update({"✅3 часа": 3})
    else:
        button.update({"3 часа": 3})

    if new_post.time == 6:
        button.update({"✅6 часов": 6})
    else:
        button.update({"6 часов": 6})

    if new_post.time == 12:
        button.update({"✅12 часов": 12})
    else:
        button.update({"12 часов": 12})

    if new_post.time == 24:
        button.update({"✅24 часа": 24})
    else:
        button.update({"24 часа": 24})

    if new_post.time == 48:
        button.update({"✅48 часов": 48})
    else:
        button.update({"48 часа": 48})

    if new_post.time == 72:
        button.update({"✅72 часа": 72})
    else:
        button.update({"72 часа": 72})

    if new_post.time == 120:
        button.update({"✅5 дней": 120})
    else:
        button.update({"5 дней": 120})

    if new_post.time == 168:
        button.update({"✅7 дней": 168})
    else:
        button.update({"7 дней": 168})

    if new_post.time == 336:
        button.update({"✅14 дней": 336})
    else:
        button.update({"14 дней": 336})

    if new_post.time == 720:
        button.update({"✅1 месяц": 720})
    else:
        button.update({"1 месяц": 720})

    if new_post.time == 0:
        button.update({"✅Не повторять": 0})
    else:
        button.update({"Не повторять": 0})

    button.update({"<< Назад": "continue", "Продолжить >>": "next_time"})
    keyboard = kb.create_keyboard(button, 3, 3, 3, 3, 1, 2)
    return keyboard


def get_kb_by_choice_channel(data: Channels, new_post: NewPost):
    button = {}
    for channel in data:
        if channel.id in new_post.channels:
            button.update({f"✅{channel.name}": f"choice_{channel.id}"})
        else:
            button.update({channel.name: f"choice_{channel.id}"})

    keyboard = kb.create_keyboard(button)
    return keyboard


def get_button(new_post: NewPost) -> dict:
    button = {}
    if new_post.protect:
        button.update({"✅Защитить контент": "protect"})
    else:
        button.update({"❌Защитить контент": "protect"})
    button.update({"Выбор групп/каналов": "choice"})
    button.update({"Автоповтор": "repeat"})
    button.update({"Отложить": "delayed"})
    button.update({"<< Назад": "back_to_create_post"})
    button.update({"Опубликовать": "s"})
    return button


@router.callback_query(lambda call: call.data == "continue" or call.data == "protect")
async def set_post(call: CallbackQuery, state: FSMContext):
    id = call.from_user.id
    user = users.get(id)
    data = await state.get_data()
    current_state = await state.get_state()
    print(current_state == "States:new_post")
    if current_state == "States:new_post":
        await state.set_state(States.new_post)
    new_post: NewPost = data["post"]
    if call.data == "protect":
        new_post.protect = not new_post.protect
    button = get_button(new_post)
    await state.update_data(post=new_post)
    await EditMessageText(chat_id=id,
                          message_id=user.message_id,
                          text="Настройте параметры публикации нового поста",
                          reply_markup=kb.create_keyboard(button, 2, 2, 2))


@router.callback_query(States.new_post, lambda call: call.data == "choice" or "choice_" in call.data)
async def choice_channel(call: CallbackQuery, state: FSMContext):
    id = call.from_user.id
    user = users.get(id)
    data = await state.get_data()
    new_post: NewPost = data["post"]
    if not new_post.channels:
        new_post.channels = [new_post.id_channel]
    if "choice_" in call.data:
        id_channel = int(call.data.replace("choice_", ""))
        if id_channel == new_post.id_channel:
            await AnswerCallbackQuery(callback_query_id=call.id, text="Нельзя удалить основной канал/группу")
            return 200
        elif id_channel in new_post.channels:
            del new_post.channels[new_post.channels.index(id_channel)]
        else:
            new_post.channels.append(id_channel)
    keyboard = get_kb_by_choice_channel(channels, new_post)
    await EditMessageText(chat_id=id,
                          message_id=user.message_id,
                          text="Выберите группы/каналы для постинга",
                          reply_markup=keyboard)
    await state.update_data(post=new_post)


@router.callback_query(States.new_post, lambda call: call.data == "repeat" or check_int(call.data))
async def choice_repeat(call: CallbackQuery, state: FSMContext):
    id = call.from_user.id
    user = users.get(id)
    data = await state.get_data()
    new_post: NewPost = data["post"]
    if check_int(call.data):
        if int(call.data) == new_post.time:
            await AnswerCallbackQuery(callback_query_id=call.id, text="Уже установлено это время")
            return 200
        new_post.time = int(call.data)
    keyboard = get_kb_time(new_post)
    await EditMessageText(chat_id=id,
                          message_id=user.message_id,
                          text="Выберите периодичность автопостинга",
                          reply_markup=keyboard)


@router.callback_query(States.new_post, lambda call: call.data == "next_time" or "duration_" in call.data)
async def choice_repeat(call: CallbackQuery, state: FSMContext):
    id = call.from_user.id
    user = users.get(id)
    data = await state.get_data()
    new_post: NewPost = data["post"]
    if call.data != "next_time":
        if "duration_" in call.data:
            duration = int(call.data.replace("duration_", ""))
        else:
            duration = new_post.duration
        if duration == new_post.duration:
            await AnswerCallbackQuery(callback_query_id=call.id, text="Уже установлено это время")
            return 200
        new_post.duration = duration
    keyboard = get_kb_duration(new_post)
    await EditMessageText(chat_id=id,
                          message_id=user.message_id,
                          text="Выберите длительнось автопостинга",
                          reply_markup=keyboard)


@router.callback_query(States.new_post, lambda call: call.data == "delayed")
async def choice_repeat(call: CallbackQuery, state: FSMContext):
    id = call.from_user.id
    user = users.get(id)
    data = await state.get_data()
    new_post: NewPost = data["post"]
    await state.set_state(States.delayed)
    await state.update_data(post=new_post)
    text = "Введите когда нужно отправить пост, в формате ЧЧ:ММ\n"
    if new_post.delayed:
        text += f"Выбранное время: {new_post.delayed}"

    await EditMessageText(chat_id=id,
                          message_id=user.message_id,
                          text=text,
                          reply_markup=kb.create_keyboard({"<< Назад": "continue"}))


@router.message(States.delayed)
async def inp_delayed(message: Message, state: FSMContext):
    id = message.from_user.id
    user = users.get(id)
    data = await state.get_data()
    new_post: NewPost = data["post"]
    await DeleteMessage(chat_id=id, message_id=message.message_id)
    if ":" in message.text:
        hour, minutes = message.text.split(":")
        if check_int(hour) and check_int(minutes):
            hour, minutes = int(hour), int(minutes)
            print(hour, minutes)
            if 0 <= hour <= 24 and 0 <= minutes <= 60:
                new_post.delayed = message.text
    button = get_button(new_post)
    await EditMessageText(chat_id=id,
                          message_id=user.message_id,
                          text="Настройте параметры публикации нового поста",
                          reply_markup=kb.create_keyboard(button, 2, 2, 2))
    await state.set_state(States.new_post)
    await state.update_data(post=new_post)


setting_post_router = router
