import asyncio
import json
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from logic import get_yasno, schedule_constructor

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

    # 1. Получаем свежие данные ОДИН раз для каждого поставщика
    # Исправлено: передаем строку "ЦЕК"/"ДТЕК", как ожидает логика внутри
    current_data_cek = get_yasno("ЦЕК")
    current_data_dtek = get_yasno("ДТЕК")

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

    # Обновляем глобальные переменные текущим состоянием
    last_api_state_cek = current_data_cek
    last_api_state_dtek = current_data_dtek

async def main():
    scheduler.add_job(check_api, 'interval', minutes=5)
    scheduler.start()

    await dp.start_polling(bot)


asyncio.run(main())

'''async def check_api():
    global last_api_state_cek, last_api_state_dtek

    current_data_cek = get_yasno("ЦЕК")
    current_data_dtek = get_yasno("ДТЕК")

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
    last_api_state_dtek = current_data_dtek'''

