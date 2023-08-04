import asyncio
import sys
from multiprocessing import Process

sys.path.append("D:/telegram_bots/creation_design_posts")
from bot.utils.send_post import SendingPost

from bot.db import postChannels
from contextlib import suppress
import logging
from bot.handlers import routers
from bot.config import bot, dp


async def main() -> None:
    for router in routers:
        dp.include_router(router)

    await dp.start_polling(bot)


class Interest_calculation:
    pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        filemode="w",
                        format="%(levelname)s %(asctime)s %(message)s",
                        encoding='utf-8')
    # data = postChannels.get_channels(id=0)
    # print(data)
    with suppress(KeyboardInterrupt):
        # asyncio.run(main())
        sendingPost = SendingPost()
        sendingPost.start_process(func=sendingPost.start_schedule)
        p0 = Process(target=asyncio.run(main()))
        p0.start()


