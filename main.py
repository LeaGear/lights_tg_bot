import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher
from datetime import datetime

from data.config import TOKEN, PROVIDERS, REFRESH_INTERVAL, RATE_LIMIT, REFRESH_INTERVAL_ALERT, KYIV_TZ
from auto_update import update
from storage import load, save, get_all_users
from logic import get_from_api, get_yasno_data
from database import session_factory, User  # Импортируем из твоего файла базы
from sqlalchemy import select, update
from handlers.user_private import user_private_router
from database import init_db
from alert import alert_groups_list


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
            await session.execute(
                update(User)
                .where(User.last_status == "Normal")
                .values(last_status="EmergencyShutdowns")
            )
            await session.commit()

            result = await session.execute(
                select(User.id, User.groups).where(User.last_status == "EmergencyShutdowns")
            )
            users_to_notify = result.all()

            for user in users_to_notify:
                # Отправляем сообщение
                header = "🚨 ЕКСТРЕНІ ВІДКЛЮЧЕННЯ 🚨\nГрафіки не діють!\nОстанній актуальний графік:\n\n"
                results = header + await get_yasno_data(user.groups)
                try:
                    await bot.send_message(user.id, results)
                    # МЕНЯЕМ ДАННЫЕ прямо в объекте
                except Exception as e:
                    logging.error(f"Failed to send message to {user.id}: {e}", exc_info=True)
                    print(f"Ошибка отправки пользователю {user.id}: {e}")
            # КОММИТИМ изменения в этом же файле
            return

        await session.execute(
            update(User)
            .where(User.last_status == "EmergencyShutdowns")
            .values(last_status="Normal")
        )
        await session.commit()

        notify = await update(provider, lst, cur)
        for list_user_and_update_message in notify:
            try:
                await bot.send_message(
                    list_user_and_update_message[0],
                    list_user_and_update_message[1]
                )
                await asyncio.sleep(RATE_LIMIT)
            except Exception as e:
                logging.error(f"Failed to send message to {list_user_and_update_message[0]}: {e}", exc_info=True)
                print(f"Ошибка отправки пользователю {list_user_and_update_message[0]}: {e}")

async def check_api():
    print("Start")
    last_api_state_cek = await load(PROVIDERS["CEK"]["file"])
    last_api_state_dtek = await load(PROVIDERS["DTEK"]["file"])

    current_data_cek = await get_from_api(PROVIDERS["CEK"]["code"], PROVIDERS["CEK"]["file"])
    current_data_dtek = await get_from_api(PROVIDERS["DTEK"]["code"], PROVIDERS["DTEK"]["file"])

    # Вызов функции в основном цикле тоже через await
    await noti("ЦЕК", last_api_state_cek, current_data_cek)
    if current_data_cek["1.1"]["today"]["status"] == "EmergencyShutdowns":
        print("EmergencyShutdowns")
    else:
        await save(current_data_cek, PROVIDERS["CEK"]["file"])

    await noti("ДТЕК", last_api_state_dtek, current_data_dtek)
    if current_data_dtek["1.1"]["today"]["status"] == "EmergencyShutdowns":
        print("EmergencyShutdowns")
    else:
        await save(current_data_dtek, PROVIDERS["DTEK"]["file"])

async def alert_for_user():
    users = await get_all_users()
    alert_groups = await alert_groups_list()
    header = f"⚠️⚠️Нагадую!⚠️⚠️ \nЧерез 15 хвилин буде відключення вашої групи/груп:\n\n"

    for user in users:
        comparisons = []
        message = header
        if user.last_status == "EmergencyShutdowns":
            continue
        #comparisons = list(set(user.groups) & set(alert_groups))
        for i in user.groups:
            for j in alert_groups:
                if i == j: comparisons.append(i)
        if comparisons:
            for gp in comparisons:
                message += f"{gp[0]} {gp[1]}\n"
            try:
                await bot.send_message(user.id, message)
            except Exception as e:
                logging.error(f"Failed to send message to {user.id}: {e}", exc_info=True)
            await asyncio.sleep(RATE_LIMIT)

async def announcement_for_all_users():
    #as123()
    print("Start announcement for all users")
    try:
        with open("data/message.txt", "r", encoding="utf-8") as f:
            message = f.read()
    except FileNotFoundError:
        print("Файл data/message.txt не найден!")
        return
    #print(message)
    list_of_all_users = await load("data/list_of_all_users.txt")

    for user in list_of_all_users:
        try:
            await bot.send_message(user, message)
        except Exception as e:
            logging.error(f"Failed to send message to {user}: {e}", exc_info=True)
            print(f"Ошибка отправки пользователю {user}: {e}")

        await asyncio.sleep(RATE_LIMIT)
    await save(message, f"data/updates/message_{datetime.now(KYIV_TZ).strftime('%d_%m_%Y_%H_%m_%s')}.txt")
    open("data/message.txt", "w").close()
    print("End announcement for all users")



async def main():
    await init_db()
    await announcement_for_all_users()
    try:
        print("Первичный сбор данных...")
        await check_api()
        print("Данные успешно подтянуты.")
    except Exception as e:
        print(f"Ошибка при старте: {e}")

    scheduler.add_job(alert_for_user, 'interval', minutes=REFRESH_INTERVAL_ALERT)
    scheduler.add_job(check_api, 'interval', minutes=REFRESH_INTERVAL)
    scheduler.start()

    await dp.start_polling(bot)


asyncio.run(main())

