import asyncio
from os import getenv

from aiogram import Bot, Dispatcher

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from handlers.user_private import user_private_router




bot = Bot(token=getenv("TOKEN"))


dp = Dispatcher()

dp.include_router(user_private_router)

async def main():
    #await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot)

asyncio.run(main())