from aiogram import F, types, Router
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from auto_update import updates
from data.config import GROUPS

from services import add_user_service, get_user_groups_message_service, get_user_groups_list_service, get_message_user_schedule_service, update_user_subscriptions_service, delete_user_subscription_service
from logic import get_info
from storage import users_table, load, save, group_from_user
#from database import session_factory, select, User
from keyboards.reply import start_kb, group_kb, ck_dtk_kb, get_keyboard

user_private_router = Router()

class AddUser(StatesGroup):
    choose_sup = State()
    choose_group = State()

class DeleteGroup(StatesGroup):
    waiting_for_choice = State()


@user_private_router.message(CommandStart()) #UPDATED
async def start_cmd(message : types.Message):
    await message.answer("Привіт, я бот, який завжди буде мати актуальний графік для тебе!😉",
                         reply_markup=start_kb)
    await add_user_service(message.from_user.id)

@user_private_router.message(F.text == "📋 Мої групи") #UPDATED
async def user_groups(message : types.Message):
    answer = await get_user_groups_message_service(message.from_user.id)
    if not answer:
        await message.answer("🟡 Ти не обрав жодної групи 🟡", reply_markup=start_kb)
    else:
        await message.answer(answer, reply_markup=start_kb)

@user_private_router.message(F.text == "🗓 Графік") #UPDATED
async def user_schedule(message : types.Message):
    answer_message = await get_message_user_schedule_service(message.from_user.id)
    if not answer_message:
        await message.answer("🟡 Ти не обрав жодної групи 🟡", reply_markup=start_kb)
    await message.answer(answer_message, reply_markup=start_kb)

@user_private_router.message(F.text == "👥 Обери групу")
async def choose_sup(message : types.Message, state: FSMContext):
    await message.answer("Обери постачальника електроенергії!",
                         reply_markup=ck_dtk_kb)
    await state.set_state(AddUser.choose_sup)

@user_private_router.message(AddUser.choose_sup, F.text.in_(["ЦЕК", "ДТЕК"]))
async def sup_save(message : types.Message, state: FSMContext):
    await state.update_data(sup=message.text)
    await message.answer("Обери свою групу!",
                         reply_markup=group_kb)
    await state.update_data(user_db_groups=await get_user_groups_list_service(message.from_user.id))
    await state.set_state(AddUser.choose_group)


@user_private_router.message(AddUser.choose_group, F.text.in_(GROUPS))
async def choose_group(message: types.Message, state: FSMContext):
    user_groups_message = ""
    user_data = await state.get_data()
    user_db_groups = user_data.get("user_db_groups", [])
    user_current_groups = user_data.get("groups_list", [])
    selected_group = f"{user_data.get('sup')}-{message.text}"
    if selected_group in user_db_groups or message.text in user_current_groups:
        await message.answer("Ця група вже є у твоєму списку! Обери іншу.")
    else:
        user_current_groups.append(message.text)
        await state.update_data(groups_list=user_current_groups)
        for i in user_current_groups:
            user_groups_message += f"{user_data.get('sup')}-{i}, "
        for i in user_db_groups:
            user_groups_message += f"{i}, "

        await message.answer(
            f"Групу {selected_group} додано! ✅\n"
            f"Твій список: {user_groups_message[:-2]}\n\n"
            "Обери ще одну або натисни кнопку 'Далі 👉', щоб зберегти.",
            reply_markup=group_kb
        )

# 3. Новый хендлер для завершения выбора (кнопка "Далі 👉")
@user_private_router.message(AddUser.choose_group, F.text == "Далі 👉")
async def finish_group_selection(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    selected_sup = user_data.get("sup", " ")
    selected_groups = user_data.get("groups_list", [])

    if not selected_groups:
        await message.answer("Ти не обрав жодної групи! Будь ласка, обери хоча б одну.")
        return

    message_with_actual_user_groups = await update_user_subscriptions_service(message.from_user.id, selected_groups, selected_sup)
    await message.answer(
        f"Дані збережено! Твої групи: {message_with_actual_user_groups}\n\n",
        reply_markup=start_kb
    )
    await state.clear()

@user_private_router.message(F.text == "❌ Видалення групи")
async def del_group(message: types.Message, state: FSMContext):
    user_groups_for_del = await get_user_groups_list_service(message.from_user.id)

    #user_groups = await group_from_user(message.from_user.id)

    if not user_groups_for_del:
        await message.answer("У тебе поки немає доданих груп.")
        return

    #list_for_key = [f"{i[0]}-{i[1]}" for i in user_groups]

    # Сохраняем список в память FSM, чтобы проверить его позже
    await state.update_data(current_groups=user_groups_for_del)
    # Переводим пользователя в состояние ожидания выбора
    await state.set_state(DeleteGroup.waiting_for_choice)

    await message.answer(
        "Оберіть групу для видалення:",
        reply_markup=get_keyboard(user_groups_for_del)
    )

@user_private_router.message(DeleteGroup.waiting_for_choice)
async def del_one_group(message: types.Message, state: FSMContext):
    data = await state.get_data()
    valid_groups = data.get("current_groups", [])

    if message.text in valid_groups:
        await delete_user_subscription_service(message.from_user.id, message.text)
        await message.answer(f"Групу {message.text} видалено!", reply_markup=start_kb)
        await state.clear()  # Сбрасываем состояние
    else:
        await message.answer("Будь ласка, обери групу за допомогою кнопок.")

@user_private_router.message(F.text == "⛔️ Видалити усі групи")
async def del_all_groups(message: types.Message):
    #async with session_factory() as session:
    #    result = await session.execute(select(User).where(User.id == str(message.from_user.id)))
    ##    user = result.scalar_one_or_none()
     #   user.groups = []
    #    await session.commit()
    #await message.answer("Усі групи видалені!")
    pass

@user_private_router.message()
async def input_error(message : types.Message):
    await message.answer("Десь помилка, розпочнемо знов!",
                         reply_markup=start_kb)