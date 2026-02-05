import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from os import getenv
from aiogram import Bot, Dispatcher

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from storage import load
from logic import schedule_constructor, get_from_api
from handlers.user_private import user_private_router

bot = Bot(token=getenv("TOKEN"))
dp = Dispatcher()
scheduler = AsyncIOScheduler()

dp.include_router(user_private_router)


async def check_api():
    print("Start")
    last_api_state_cek = load("cek.json")
    last_api_state_dtek = load("dtek.json")

    current_data_cek = get_from_api(303, "cek.json")
    current_data_dtek = get_from_api(301, "dtek.json")

    # Функция для обработки рассылки, чтобы не дублировать код
    async def notify_users(provider_name, current_data, last_state):
        # Проверяем: есть ли старое состояние и изменилось ли оно сейчас
        if last_state and current_data != last_state:
            users = load("users.json")
            # Фильтруем пользователей, которым нужно обновление по этому провайдеру
            for user in users:
                if user.get("sup") == provider_name:
                    for group in user["group"]:
                        try:
                            # Формируем график (здесь можно еще оптимизировать, передавая уже скачанные данные)
                            mess = schedule_constructor(f"Група {group} {provider_name}",
                                                        current_data[group]["today"]["slots"],'')
                            await bot.send_message(user["id"], f"❗️❗️УВАГА❗️ ОНОВЛЕННЯ ГРАФІКУ "
                                                               f"{provider_name}❗️❗\n{mess}")
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

