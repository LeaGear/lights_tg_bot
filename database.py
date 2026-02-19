import json
from sqlalchemy import Column, String, Boolean, JSON, select
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from data.config import DB_URL

# 1. Сериализатор для работы с кириллицей в JSON
def my_serializer(obj):
    return json.dumps(obj, ensure_ascii=False)


# 2. Асинхронный движок для работы бота
# ВАЖНО: sqlite+aiosqlite
engine = create_async_engine(
    DB_URL,
    json_serializer=my_serializer
)

# 3. Фабрика асинхронных сессий
session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    #sup = Column(String)
    groups = Column(JSON)
    notifications = Column(Boolean, default=True)
    last_status = Column(String, default="Normal")


# 4. Асинхронная инициализация базы
async def init_db():
    async with engine.begin() as conn:
        # Используем run_sync для синхронной команды создания таблиц
        await conn.run_sync(Base.metadata.create_all)


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