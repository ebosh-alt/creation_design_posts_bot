import asyncio
import time
from multiprocessing import Process

from aiogram.types import FSInputFile
from schedule import run_pending
from aiogram.methods import SendMessage, SendPhoto, SendVideo, SendAnimation

from bot.const import TypeFile
from bot.db import Posts
from bot.db import users, channels, Channels, Post, postChannels, PostChannel, File, media, UrlButton, posts, \
    urlButtons, hiddenButtons, HiddenButton

from bot import keyboards as kb
from bot.config import bot


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


def send_post():
    post: Post = posts.get(2737)
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

    for id in id_channels:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            send(id=id, text=post.text, protect_content=post.protect, keyboard=keyboard, send_media=send_media))


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
        send_post()

    def start_schedule(self):
        while True:
            self.work()
            time.sleep(10)



