
from aiogram import F, types, Router
from aiogram.filters import CommandStart
from logic import get_yasno_data, get_info
from storage import users_table

from keyboards.reply import start_kb, group_kb,ck_dtk_kb
user_private_router = Router()

data = {"id": "", "sup": "", "group": ""}
groups = ["1.1", "1.2", "2.1", "2.2", "3.1", "3.2", "4.1", "4.2", "5.1", "5.2", "6.1", "6.2",]

@user_private_router.message(CommandStart())
async def start_cmd(message : types.Message):
    await message.answer("Hi, I`m shutdown schedule helper!",
                         reply_markup=start_kb)


@user_private_router.message(F.text == "👥 Choose group")
async def choose_sup(message : types.Message):
    await message.answer("Choose electricity supplier",
                         reply_markup=ck_dtk_kb)

@user_private_router.message(F.text == "🗓 Schedule")
async def schedule(message : types.Message):
    await message.answer("Your schedule!",
                         reply_markup=start_kb)
    graph = get_info(message.from_user.id)
    await message.answer(graph)

@user_private_router.message(F.text.in_(["CEK", "DTEK"]))
async def sup_save(message : types.Message):
    data["id"] = str(message.from_user.id)
    data["sup"] = message.text
    await message.answer("Choose a group!",
                         reply_markup=group_kb)

@user_private_router.message(F.text.in_(groups))
async def choose_group(message : types.Message):
    data["group"] = message.text
    print(data)
    users_table(data)
    await message.answer("Data receive!",
                         reply_markup=start_kb)

@user_private_router.message()
async def input_error(message : types.Message):
    await message.answer("Incorrect input!",
                         reply_markup=start_kb)