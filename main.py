import asyncio
import json
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from logic import get_yasno, get_yasno_data

from os import getenv
from aiogram import Bot, Dispatcher

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from handlers.user_private import user_private_router


bot = Bot(token=getenv("TOKEN"))
dp = Dispatcher()
scheduler = AsyncIOScheduler()

dp.include_router(user_private_router)

last_api_state_cek = {}
last_api_state_dtek = {}

async def check_api():
    global last_api_state_cek, last_api_state_dtek

    current_data_cek = get_yasno(303)
    current_data_dtek = get_yasno(301)

    if last_api_state_cek and current_data_cek != last_api_state_cek:
        with open('data.json', 'r') as f:
            users = json.load(f)
        user_dict = []
        for i in users:
            if i["notifications"] and i["sup"] == "ЦЕК":
                user_dict.append(i)
        for item in user_dict:
            try:
                mess = get_yasno_data(item["sup"], item["group"])
                await bot.send_message(item["id"], f"❗️❗️УВАГА❗️ ОНОВЛЕННЯ ГРАФІКУ❗️❗\n{mess}")
            except Exception:
                pass

    if last_api_state_dtek and current_data_dtek != last_api_state_dtek:
        with open('data.json', 'r') as f:
            users = json.load(f)
        user_dict = []
        for i in users:
            if i["notifications"] and i["sup"] == "ДТЕК":
                user_dict.append(i)
        for item in user_dict:
            try:
                mess = get_yasno_data(item["sup"], item["group"])
                await bot.send_message(item["id"], f"❗️❗️УВАГА❗️ ОНОВЛЕННЯ ГРАФІКУ❗️❗️\n{mess}")
            except Exception:
                pass

    last_api_state_cek = current_data_cek
    last_api_state_dtek = current_data_dtek

async def main():
    scheduler.add_job(check_api, 'interval', minutes=5)
    scheduler.start()

    await dp.start_polling(bot)


asyncio.run(main())