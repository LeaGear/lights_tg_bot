from aiogram import F, types, Router
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from logic import get_info
from storage import users_table, auto_update

from keyboards.reply import start_kb, group_kb, ck_dtk_kb, update_kb
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
async def choose_group(message : types.Message, state: FSMContext):
    user_data = await state.get_data()
    final_data = {
        "id": str(message.from_user.id),
        "sup": user_data["sup"],
        "group": message.text,
        "notifications": True
    }
    print(final_data)
    users_table(final_data)
    await message.answer("Дані отримано, я тебе запамʼятав!",
                         reply_markup=start_kb)
    await state.clear()

@user_private_router.message(F.text == "🔄 Автооновлення")
async def auto_upd(message : types.Message):
    await message.answer("Чи бажаєшь ввімкнути автооновлення?!",
                         reply_markup=update_kb)

@user_private_router.message(F.text == "🟢 Увімкнути")
async def auto_update_on(message : types.Message):
    auto_update(message.from_user.id, 1)
    await message.answer("🟢Оновлення - УВІМКНУТІ🟢",
                         reply_markup=start_kb)

@user_private_router.message(F.text == "🔴 Вимкнути")
async def auto_update_off(message : types.Message):
    auto_update(message.from_user.id, 0)
    await message.answer("🔴Оновлення - ВИМКНУТІ🔴",
                         reply_markup=start_kb)

@user_private_router.message(F.text == "Errrrror404!")
async def error_404(message : types.Message):
    await message.answer("Щось сталося, нажаль немає актуальних даних!\nСпробуйте пізніше!",
                         reply_markup=start_kb)

@user_private_router.message()
async def input_error(message : types.Message):
    await message.answer("Десь помилка, розпочнемо знов!",
                         reply_markup=start_kb)