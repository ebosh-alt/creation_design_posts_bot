import asyncio
import datetime
import time
from multiprocessing import Process

from aiogram.types import FSInputFile

from bot import keyboards as kb
from bot.config import bot
from bot.const import TypeFile
from bot.db import Post, postChannels, media, posts, urlButtons, hiddenButtons


async def send(id: int, text: str, protect_content: bool, keyboard, send_media):
    if send_media:
        file = FSInputFile(send_media[1])
        type_file = TypeFile(send_media[2])
        location = bool(send_media[3])
        match type_file:
            case TypeFile.Photo:
                await bot.send_photo(chat_id=id,
                                     caption=text,
                                     photo=file,
                                     reply_markup=keyboard
                                     )

            case TypeFile.Video:
                await bot.send_video(chat_id=id,
                                     caption=text,
                                     video=file,
                                     reply_markup=keyboard
                                     )

            case _:
                if location:
                    await bot.send_message(chat_id=id,
                                           text=text,
                                           reply_markup=keyboard)
                    await bot.send_animation(chat_id=id,
                                             caption=text,
                                             animation=file
                                             )

                else:
                    await bot.send_animation(chat_id=id,
                                             caption=text,
                                             animation=file
                                             )
                    await bot.send_message(chat_id=id,
                                           text=text,
                                           reply_markup=keyboard)

    else:
        await bot.send_message(chat_id=id,
                               text=text,
                               protect_content=protect_content,
                               reply_markup=keyboard)


def get_info_post(post: Post = None):
    if post is None:
        post: Post = posts.get(2835)
    id_channels = postChannels.get_channels(post.id)
    send_media = None
    hidden_button = None
    url_button = None
    if post.media:
        send_media = media.get_media(post.id)
    if post.button:
        hidden_button = hiddenButtons.get_button(post.id)
        url_button = urlButtons.get_button(post.id)
    keyboard = None
    send_buttons = {}
    sizes_but = []
    if url_button:
        sizes = url_button[0][3].split(" ")
        sizes_but = []
        for i in sizes:
            sizes_but.append(int(i))
        for but in url_button:
            send_buttons.update({but[1]: but[2]})
    if hidden_button:
        send_buttons.update({hidden_button[1]: hidden_button[0]})
    if send_buttons:
        keyboard = kb.create_keyboard(send_buttons, sizes_but)
    return post.text, post.protect, keyboard, send_media, id_channels


def sending(post):
    data = get_info_post(post)
    text = data[0]
    protect = data[1]
    keyboard = data[2]
    send_media = data[3]
    id_channels = data[4]
    for id in id_channels:
        loop = asyncio.get_event_loop()

        loop.run_until_complete(
            send(id=id, text=text, protect_content=protect, keyboard=keyboard, send_media=send_media))


def check():
    now_time = datetime.datetime.utcnow()
    for post in posts:
        if post.send_time:
            send_time = datetime.datetime.utcfromtimestamp(post.send_time)
            if now_time.hour == send_time.hour and now_time.minute == send_time.minute:
                sending(post)
                end_posting = datetime.datetime.utcfromtimestamp(post.end_posting)
                if end_posting.day == now_time.day and end_posting.hour == now_time.hour and \
                        end_posting.minute == now_time.minute and post.end_posting != 0:
                    post.send_time = 0
                else:
                    post.send_time = now_time + datetime.timedelta(hours=post.time)
                    post.send_time = post.send_time.timestamp()
                posts.update(post)


class SendingPost:
    def __init__(self) -> None:
        self.p0 = Process()

    def start_process(self, func, arg=None):
        if arg is not None:
            self.p0 = Process(target=func, args=(arg,))
        else:
            self.p0 = Process(target=func)
        self.p0.start()

    def stop_process(self):
        self.p0.terminate()

    @staticmethod
    def work():
        check()
        # send_post()

    def start_schedule(self):
        while True:
            self.work()
            time.sleep(10)
