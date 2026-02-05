import asyncio
import json
import requests

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from os import getenv
from aiogram import Bot, Dispatcher

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from logic import schedule_constructor
from handlers.user_private import user_private_router

bot = Bot(token=getenv("TOKEN"))
dp = Dispatcher()
scheduler = AsyncIOScheduler()

dp.include_router(user_private_router)


async def check_api():
    print("Start")
    try:
        with open("cek.json", "r", encoding="utf-8") as last_data_cek:
            last_api_state_cek = json.load(last_data_cek)
            #print("dat", last_api_state_cek)
        with open("dtek.json", "r", encoding="utf-8") as last_data_dtek:
            last_api_state_dtek = json.load(last_data_dtek)
            #print("dat2", last_api_state_dtek)
    except FileNotFoundError:
        print("Create new file!")

    url = "https://app.yasno.ua/api/blackout-service/public/shutdowns/regions/3/dsos/303/planned-outages"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        current_data_cek = data
        #print(data)
    else:
        current_data_cek = {}
        return "Yasno - DIE!"

    with open("cek.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print("CEK schedule saved successfully!")

    url1 = "https://app.yasno.ua/api/blackout-service/public/shutdowns/regions/3/dsos/301/planned-outages"
    response1 = requests.get(url1)

    if response1.status_code == 200:
        data = response1.json()
        current_data_dtek = data
        #print(data)
    else:
        current_data_dtek = {}
        return "Yasno - DIE!"
    with open("dtek.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print("DTEK schedule saved successfully!")

    # Функция для обработки рассылки, чтобы не дублировать код
    async def notify_users(provider_name, current_data, last_state):
        # Проверяем: есть ли старое состояние и изменилось ли оно сейчас
        if last_state and current_data != last_state:
            try:
                with open('data.json', 'r', encoding='utf-8') as f:
                    users = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                return # Если файла нет или он битый, выходим

            # Фильтруем пользователей, которым нужно обновление по этому провайдеру
            for user in users:
                if user.get("notifications") and user.get("sup") == provider_name:
                    try:
                        # Формируем график (здесь можно еще оптимизировать, передавая уже скачанные данные)
                        mess = schedule_constructor(f"Група {user['group']} {provider_name}",
                                                    current_data[user["group"]]["today"]["slots"],'')
                        await bot.send_message(user["id"], f"❗️❗️УВАГА❗️ ОНОВЛЕННЯ ГРАФІКУ {provider_name}❗️❗\n{mess}")
                        # Небольшая пауза, чтобы Telegram не забанил за спам
                        await asyncio.sleep(0.05)
                    except Exception as e:
                        print(f"Ошибка отправки пользователю {user['id']}: {e}")

    # Запускаем проверку для обоих провайдеров
    await notify_users("ЦЕК", current_data_cek, last_api_state_cek)
    await notify_users("ДТЕК", current_data_dtek, last_api_state_dtek)




async def main():
    try:
        print("Первичный сбор данных...")
        await check_api()
        print("Данные успешно подтянуты.")
    except Exception as e:
        print(f"Ошибка при старте: {e}")

    scheduler.add_job(check_api, 'interval', minutes=5)
    scheduler.start()

    await dp.start_polling(bot)


asyncio.run(main())

