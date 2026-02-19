from aiogram import F, types, Router
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from logic import get_info
from storage import users_table, load, save, group_from_user
from database import del_group_from_db, session_factory, select, User
from keyboards.reply import start_kb, group_kb, ck_dtk_kb, get_keyboard
from data.config import GROUPS

user_private_router = Router()

class AddUser(StatesGroup):
    choose_sup = State()
    choose_group = State()

class DeleteGroup(StatesGroup):
    waiting_for_choice = State()


@user_private_router.message(CommandStart())
async def start_cmd(message : types.Message):
    await message.answer("Привіт, я бот, який завжди буде мати актуальний графік для тебе!😉",
                         reply_markup=start_kb)

@user_private_router.message(F.text == "📋 Мої групи")
async def schedule(message : types.Message):
    groups_for_watching = await group_from_user(message.from_user.id)
    if groups_for_watching:
        mess = "📜Ось список груп за якими ти слідкуєш!📜\n\n"
        for i in groups_for_watching:
            mess += f"{i[0]}-{i[1]}, "
        await message.answer(mess[:-2], reply_markup=start_kb)
    else:
        await message.answer("🟡 Ти не обрав жодної групи 🟡")


@user_private_router.message(F.text == "🗓 Графік")
async def schedule(message : types.Message):
    graph = await get_info(message.from_user.id)
    await message.answer(graph, reply_markup=start_kb)

@user_private_router.message(F.text == "👥 Обери групу")
async def choose_sup(message : types.Message, state: FSMContext):
    await message.answer("Обери постачальника електроенергії!",
                         reply_markup=ck_dtk_kb)
    await state.set_state(AddUser.choose_sup)

@user_private_router.message(AddUser.choose_sup, F.text.in_(["ЦЕК", "ДТЕК"]))
async def sup_save(message : types.Message, state: FSMContext):
    await state.update_data(sup = message.text)
    await message.answer("Обери свою групу!",
                         reply_markup=group_kb)
    await state.set_state(AddUser.choose_group)


@user_private_router.message(AddUser.choose_group, F.text.in_(GROUPS))
async def choose_group(message: types.Message, state: FSMContext):
    # 1. Берем текущие данные из FSM
    user_data = await state.get_data()
    message_group = ""
    # 2. Достаем список групп (если его еще нет — создаем пустой)
    user_gp = user_data.get("groups_list", [])
    #print(user_gp)
    if not user_gp:
        #print("path 1")
        selected_groups = await group_from_user(message.from_user.id)
    else:
        #print("path 2")
        selected_groups = user_gp
    #print(selected_groups)
    user_group = [user_data["sup"], message.text]

    if user_group not in selected_groups:
        selected_groups.append(user_group)
        #print("selected_groups - ", selected_groups)
        # Сохраняем обновленный список в память
        await state.update_data(groups_list=selected_groups)
        #print(selected_groups)
        for i in selected_groups:
            message_group += f"{i[0]}-{i[1]}, "

        await message.answer(
            f"Групу {user_group[0]}-{user_group[1]} додано! ✅\n"
            f"Твій список: {message_group[:-2]}\n\n"
            "Обери ще одну або натисни кнопку 'Далі 👉', щоб зберегти.",
            reply_markup=group_kb  # Тут должна быть кнопка "Далі 👉"
        )
    else:
        await message.answer("Ця група вже є у твоєму списку! Обери іншу.")


# 3. Новый хендлер для завершения выбора (кнопка "Далі 👉")
@user_private_router.message(AddUser.choose_group, F.text == "Далі 👉")
async def finish_group_selection(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    selected_groups = user_data.get("groups_list", [])
    #print(selected_groups)
    message_group = ""

    if not selected_groups:
        await message.answer("Ти не обрав жодної групи! Будь ласка, обери хоча б одну.")
        return

    # Формируем итоговый словарь (теперь со списком)
    final_data = {
        "id": str(message.from_user.id),
        "group": selected_groups,  # ТЕПЕРЬ ЭТО СПИСОК
        "notifications": True
    }
    await users_table(final_data)

    for i in selected_groups:
        message_group += f"{i[0]}-{i[1]}, "
    await message.answer(
        f"Дані збережено! Твої групи: {message_group[:-2]}\n\n",
        reply_markup=start_kb
    )
    await state.clear()

    list_of_all_users = await load("data/list_of_all_users.txt")
    if not str(message.from_user.id) in list_of_all_users:
        list_of_all_users.append(str(message.from_user.id))
    await save(list_of_all_users, "data/list_of_all_users.txt")

@user_private_router.message(F.text == "❌ Видалення групи")
async def del_group(message: types.Message, state: FSMContext):
    user_groups = await group_from_user(message.from_user.id)

    if not user_groups:
        await message.answer("У тебе поки немає доданих груп.")
        return

    list_for_key = [f"{i[0]}-{i[1]}" for i in user_groups]

    # Сохраняем список в память FSM, чтобы проверить его позже
    await state.update_data(current_groups=list_for_key)
    # Переводим пользователя в состояние ожидания выбора
    await state.set_state(DeleteGroup.waiting_for_choice)

    await message.answer(
        "Оберіть групу для видалення:",
        reply_markup=get_keyboard(list_for_key)
    )

@user_private_router.message(DeleteGroup.waiting_for_choice)
async def del_one_group(message: types.Message, state: FSMContext):
    data = await state.get_data()
    valid_groups = data.get("current_groups", [])

    if message.text in valid_groups:
        # Тут твоя логика удаления из базы
        # Например: remove_group_from_db(message.from_user.id, message.text)
        target = message.text.split("-")
        await del_group_from_db(message.from_user.id, target)
        await message.answer(f"Групу {message.text} видалено!", reply_markup=start_kb)
        await state.clear()  # Сбрасываем состояние
    else:
        await message.answer("Будь ласка, обери групу за допомогою кнопок.")

@user_private_router.message(F.text == "⛔️ Видалити усі групи")
async def del_all_groups(message: types.Message):
    async with session_factory() as session:
        result = await session.execute(select(User).where(User.id == str(message.from_user.id)))
        user = result.scalar_one_or_none()
        user.groups = []
        await session.commit()
    await message.answer("Усі групи видалені!")

@user_private_router.message()
async def input_error(message : types.Message):
    await message.answer("Десь помилка, розпочнемо знов!",
                         reply_markup=start_kb)