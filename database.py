import json
from datetime import datetime

from sqlalchemy import String, BigInteger, UniqueConstraint, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncConnection
from sqlalchemy.dialects.postgresql import JSONB

from data.config import DB_URL

# 1. Сериализатор для работы с кириллицей в JSON
def my_serializer(obj):
    return json.dumps(obj, ensure_ascii=False)


# 2. Асинхронный движок для работы бота
engine = create_async_engine(
    DB_URL,
    echo=False,
    pool_pre_ping=True,
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
    id : Mapped[int] = mapped_column(primary_key=True)
    telegram_id : Mapped[int] = mapped_column(BigInteger, unique=True)

class OutageGroup(Base):
    __tablename__ = "outage_groups"
    __table_args__ = (UniqueConstraint("provider", "queue"),)
    id : Mapped[int] = mapped_column(primary_key=True)
    provider : Mapped[str] = mapped_column(String(20))
    queue : Mapped[str] = mapped_column(String(10))
    today_schedule_hash : Mapped[str | None] = mapped_column(String(64))
    today_schedule_json : Mapped[dict | None] = mapped_column(JSONB)
    schedule_actuality : Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

class Subscription(Base):
    __tablename__ = "subscriptions"
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    group_id : Mapped[int] = mapped_column(ForeignKey("outage_groups.id", ondelete="CASCADE"), primary_key=True)
    last_notified_hash : Mapped[str | None] = mapped_column(String(64))
