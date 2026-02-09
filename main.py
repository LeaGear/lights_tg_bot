import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from os import getenv
from aiogram import Bot, Dispatcher

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv("data/.env"))

from storage import load, get_all_users
from logic import schedule_constructor, get_from_api
from handlers.user_private import user_private_router
from database import Session, User

bot = Bot(token=getenv("TOKEN"))
dp = Dispatcher()
scheduler = AsyncIOScheduler()

dp.include_router(user_private_router)


async def check_api():
    print("Start")
    last_api_state_cek = load("data/cek.json")
    last_api_state_dtek = load("data/dtek.json")

    current_data_cek = get_from_api(303, "data/cek.json")
    current_data_dtek = get_from_api(301, "data/dtek.json")

    # Функция для обработки рассылки, чтобы не дублировать код
    async def notify_users(provider_name, current_data, last_state):
        # Проверяем: есть ли старое состояние и изменилось ли оно сейчас

        if not last_state or current_data == last_state:
            return

        users = get_all_users()
        session = Session()
        # Фильтруем пользователей, которым нужно обновление по этому провайдеру
        for user_obj in users:
            user = session.get(User, user_obj.id)

            if user.sup == provider_name and user.groups:
                send_update = False
                is_emergency = False
                all_messages = []

                for group in user.groups:
                    # Проверяем статус именно ЭТОЙ группы
                    new_status = current_data.get(group, {}).get("today", {}).get("status")
                    old_status = user.last_status

                    if new_status == "EmergencyShutdowns":
                        is_emergency = True
                        # При экстренных шлем старый график как ориентир
                        if old_status != "EmergencyShutdowns":
                            send_update = True
                            mess = schedule_constructor(
                                f"Група {group} {provider_name}",
                                last_state[group]["today"]["slots"],
                                '')
                            all_messages.append(mess)

                    elif new_status != old_status:
                        # Статус изменился (например, с Emergency на Normal)
                        send_update = True
                        slots = current_data[group]["today"]["slots"]
                        all_messages.append(schedule_constructor(f"Група {group}",
                                                                 slots, ''))

                if send_update and all_messages:
                    # Собираем финальный текст
                    user.last_status = "EmergencyShutdowns" if is_emergency else "Normal"
                    separator = "\n" + "━" * 20 + "\n"
                    final_text = separator.join(all_messages)

                    header = ("🚨 <b>ЕКСТРЕНІ ВІДКЛЮЧЕННЯ</b> 🚨\nГрафіки не діють!\n"
                              "Останній актуальний графік!\n"
                              f"Дата останнього оновлення: {last_state["1.1"]["today"]["date"][:10]}") if is_emergency \
                        else f"❗️❗️ <b>УВАГА! ОНОВЛЕННЯ ГРАФІКУ {provider_name}</b> ❗️❗"

                    try:
                        await bot.send_message(
                            user.id,
                            f"{header}\n\n{final_text}",
                            parse_mode="HTML"
                        )
                        session.commit()
                        await asyncio.sleep(0.05)  # Защита от спам-фильтра Telegram
                    except Exception as e:
                        print(f"Ошибка отправки пользователю {user.id}: {e}")
        session.close()

    # Запускаем проверку для обоих провайдеров
    await notify_users("ЦЕК", current_data_cek, last_api_state_cek)
    await notify_users("ДТЕК", current_data_dtek, last_api_state_dtek)

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
            await bot.send_message(user, f"ОГОЛОШЕННЯ. УВАГА!\n\n{message}")
        except Exception as e:
            print(f"Ошибка отправки пользователю {user}: {e}")
    print("End announcement for all users")



async def main():

    #await announcement_for_all_users()

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

