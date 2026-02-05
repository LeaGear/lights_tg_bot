from aiogram import F, types, Router
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from logic import get_info
from storage import users_table

from keyboards.reply import start_kb, group_kb, ck_dtk_kb
user_private_router = Router()

groups = ["1.1", "1.2", "2.1", "2.2", "3.1", "3.2", "4.1", "4.2", "5.1", "5.2", "6.1", "6.2",]

class Add_user(StatesGroup):
    choose_sup = State()
    choose_group = State()


@user_private_router.message(CommandStart())
async def start_cmd(message : types.Message):
    await message.answer("Привіт, я бот, який завжди буде мати актуальний графік для тебе!😉",
                         reply_markup=start_kb)


@user_private_router.message(F.text == "👥 Обери групу")
async def choose_sup(message : types.Message, state: FSMContext):
    await message.answer("Обери постачальника електроенергії!",
                         reply_markup=ck_dtk_kb)
    await state.set_state(Add_user.choose_sup)

@user_private_router.message(F.text == "🗓 Графік")
async def schedule(message : types.Message):
    await message.answer("🗓Ну що ж, подивимось!🗓",
                         reply_markup=start_kb)
    graph = get_info(message.from_user.id)
    await message.answer(graph)

@user_private_router.message(Add_user.choose_sup, F.text.in_(["ЦЕК", "ДТЕК"]))
async def sup_save(message : types.Message, state: FSMContext):
    await state.update_data(sup = message.text)
    await message.answer("Обери свою групу!",
                         reply_markup=group_kb)
    await state.set_state(Add_user.choose_group)


@user_private_router.message(Add_user.choose_group, F.text.in_(groups))
async def choose_group(message: types.Message, state: FSMContext):
    # 1. Берем текущие данные из FSM
    user_data = await state.get_data()

    # 2. Достаем список групп (если его еще нет — создаем пустой)
    selected_groups = user_data.get("groups_list", [])

    if message.text not in selected_groups:
        selected_groups.append(message.text)
        # Сохраняем обновленный список в память
        await state.update_data(groups_list=selected_groups)

        await message.answer(
            f"Групу {message.text} додано! ✅\n"
            f"Твій список: {', '.join(selected_groups)}\n\n"
            "Обери ще одну або натисни кнопку 'Далі 👉', щоб зберегти.",
            reply_markup=group_kb  # Тут должна быть кнопка "Далі 👉"
        )
    else:
        await message.answer("Ця група вже є у твоєму списку! Обери іншу.")


# 3. Новый хендлер для завершения выбора (кнопка "Далі 👉")
@user_private_router.message(Add_user.choose_group, F.text == "Далі 👉")
async def finish_group_selection(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    selected_groups = user_data.get("groups_list", [])

    if not selected_groups:
        await message.answer("Ти не обрав жодної групи! Будь ласка, обери хоча б одну.")
        return

    # Формируем итоговый словарь (теперь с списком)
    final_data = {
        "id": str(message.from_user.id),
        "sup": user_data["sup"],
        "group": selected_groups,  # ТЕПЕРЬ ЭТО СПИСОК
        "notifications": True
    }

    users_table(final_data)
    await message.answer(
        f"Дані збережено! Твої групи: {', '.join(selected_groups)}",
        reply_markup=start_kb
    )
    await state.clear()
'''@user_private_router.message(Add_user.choose_group, F.text.in_(groups))
async def choose_group(message : types.Message, state: FSMContext):
    user_data = await state.get_data()
    final_data = {
        "id": str(message.from_user.id),
        "sup": user_data["sup"],
        "group": message.text
    }
    print(final_data)
    users_table(final_data)
    await message.answer("Дані отримано, я тебе запамʼятав!",
                         reply_markup=start_kb)
    await state.clear()'''

@user_private_router.message()
async def input_error(message : types.Message):
    await message.answer("Десь помилка, розпочнемо знов!",
                         reply_markup=start_kb)