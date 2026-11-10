
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from database import session_factory, User, OutageGroup, Subscription


async def add_user_db(telegram_id: int):
    async with session_factory() as session:
        await session.execute(
            insert(User)
            .values(telegram_id=telegram_id)
            .on_conflict_do_nothing(index_elements=[User.telegram_id])
        )
        await session.commit()
        return await session.execute(select(User).where(User.telegram_id == telegram_id))

# 5. Функция удаления группы
async def del_group_from_db(user_id: int, target_list: list):
    async with session_factory() as session:
        result = await session.execute(select(User).where(User.id == str(user_id)))
        user = result.scalar_one_or_none()

        if user and user.groups:
            # Оставляем только те группы, которые не совпадают с удаляемой
            user.groups = [g for g in user.groups if g != target_list]

            # Сообщаем SQLAlchemy, что список внутри JSON изменился
            flag_modified(user, "groups")

            await session.commit()