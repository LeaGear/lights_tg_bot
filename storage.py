import json

from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified

from database import session_factory, User


async def group_from_user(uid):
    async with session_factory() as session:
        result = await session.execute(select(User).where(User.id == str(uid)))
        user = result.scalar_one_or_none()
        return user.groups if user else []

async def get_all_users():
    async with session_factory() as session:
        result = await session.execute(select(User))
        return result.scalars().all()

async def users_table(data):
    # Используем асинхронный контекстный менеджер (async with)
    # Это само закроет сессию, поэтому session.close() не нужен
    async with session_factory() as session:
        uid = data["id"]
        # Используем await и асинхронный запрос
        result = await session.execute(select(User).filter(User.id == str(uid)))
        user = result.scalar_one_or_none()

        if user:
            user.groups = data["group"]
            user.notifications = data["notifications"]
        else:
            new_user = User(id=str(uid), groups=data["group"], notifications=data["notifications"])
            session.add(new_user)

        # ОБЯЗАТЕЛЬНО await перед commit
        await session.commit()

def load(file_name):
    all_data = []
    try:
        with open(file_name, "r", encoding="utf-8") as file1:
            all_data = json.load(file1)
    except FileNotFoundError:
        print("Create new file!")
    return all_data

def save(all_data, file_name):
    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(all_data, file, ensure_ascii=False, indent=2)
    print("Operation saved successfully!")
    #print(all_data)
