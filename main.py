import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher


from data.config import TOKEN, PROVIDERS, REFRESH_INTERVAL, RATE_LIMIT
from auto_update import update
from storage import load, save
from logic import get_from_api, get_yasno_data
from database import session_factory, User  # Импортируем из твоего файла базы
from sqlalchemy import select
from handlers.user_private import user_private_router
from database import init_db

bot = Bot(token=TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

dp.include_router(user_private_router)


async def noti(provider, lst, cur):
    async with session_factory() as session:
        # print("Starting notify!")
        if lst == cur:
            # print(f"Last status == current status {provider}!")
            return

        if cur["1.1"]["today"]["status"] == "EmergencyShutdowns":
            # Получаем пользователей, которым нужно сменить статус
            result = await session.execute(
                select(User).where(User.last_status == "Normal")
            )
            users = result.scalars().all()
            for user in users:
                # Отправляем сообщение
                header = "🚨 ЕКСТРЕНІ ВІДКЛЮЧЕННЯ 🚨\nГрафіки не діють!\nОстанній актуальний графік:\n\n"
                results = header + get_yasno_data(user.groups)
                try:
                    await bot.send_message(user.id, results)
                    # МЕНЯЕМ ДАННЫЕ прямо в объекте
                    user.last_status = "EmergencyShutdowns"
                except Exception as e:
                    print(f"Ошибка отправки пользователю {user.id}: {e}")
            # КОММИТИМ изменения в этом же файле
            await session.commit()
            return

        result = await session.execute(
            select(User).where(User.last_status == "EmergencyShutdowns")
        )
        users = result.scalars().all()
        for user in users:
            user.last_status = "Normal"
        await session.commit()
        # print(f"LAst status = normal and update {provider}")

        notify = await update(provider, lst, cur)
        for list_user_and_update_message in notify:
            try:
                await bot.send_message(
                    list_user_and_update_message[0],
                    list_user_and_update_message[1]
                )
                await asyncio.sleep(RATE_LIMIT)
            except Exception as e:
                print(f"Ошибка отправки пользователю {list_user_and_update_message[0]}: {e}")

async def check_api():
    print("Start")
    last_api_state_cek = load(PROVIDERS["CEK"]["file"])
    last_api_state_dtek = load(PROVIDERS["DTEK"]["file"])

    current_data_cek = await get_from_api(PROVIDERS["CEK"]["code"], PROVIDERS["CEK"]["file"])
    current_data_dtek = await get_from_api(PROVIDERS["DTEK"]["code"], PROVIDERS["DTEK"]["file"])

    # Вызов функции в основном цикле тоже через await
    await noti("ЦЕК", last_api_state_cek, current_data_cek)
    if current_data_cek["1.1"]["today"]["status"] == "EmergencyShutdowns":
        print("EmergencyShutdowns")
    else:
        save(current_data_cek, PROVIDERS["CEK"]["file"])

    await noti("ДТЕК", last_api_state_dtek, current_data_dtek)
    if current_data_dtek["1.1"]["today"]["status"] == "EmergencyShutdowns":
        print("EmergencyShutdowns")
    else:
        save(current_data_dtek, PROVIDERS["DTEK"]["file"])



async def announcement_for_all_users():
    print("Start announcement for all users")
    try:
        with open("data/message.txt", "r", encoding="utf-8") as f:
            message = f.read()
    except FileNotFoundError:
        print("Файл data/message.txt не найден!")
        return
    print(message)
    list_of_all_users = load("data/list_of_all_users.txt")

    for user in list_of_all_users:
        try:
            await bot.send_message(user, message)
        except Exception as e:
            print(f"Ошибка отправки пользователю {user}: {e}")

        await asyncio.sleep(RATE_LIMIT)

    print("End announcement for all users")



async def main():
    await init_db()
    #await announcement_for_all_users()
    try:
        print("Первичный сбор данных...")
        await check_api()
        print("Данные успешно подтянуты.")
    except Exception as e:
        print(f"Ошибка при старте: {e}")

    scheduler.add_job(check_api, 'interval', minutes=REFRESH_INTERVAL)
    scheduler.start()

    await dp.start_polling(bot)


asyncio.run(main())

