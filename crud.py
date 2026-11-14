from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert
from database import session_factory, User, OutageGroup, Subscription
from exceptions import UnknownGroupError

async def add_user_db(telegram_id: int):
    async with session_factory() as session:
        await session.execute(
            insert(User)
            .values(telegram_id=telegram_id)
            .on_conflict_do_nothing(index_elements=[User.telegram_id])
        )
        await session.commit()
        return await session.execute(select(User).where(User.telegram_id == telegram_id))

async def get_user_groups_db(telegram_id: int) -> list:
    async with session_factory() as session:
        result = await session.scalars(
            select(OutageGroup)
            .join(Subscription, Subscription.group_id == OutageGroup.id)
            .join(User, User.id == Subscription.user_id)
            .where(User.telegram_id==telegram_id)
        )
        return list(result.all())

async def add_user_subs_db(telegram_id: int, queue: str, provider: str):
    async with session_factory() as session:
        user_id = await session.scalar(
            select(User.id).where(User.telegram_id == telegram_id)
        )
        group_id = await session.scalar(
            select(OutageGroup.id).where(OutageGroup.queue == queue,
                                      OutageGroup.provider == provider)
        )

        if group_id is None:
            await session.rollback()
            raise UnknownGroupError(group_id)

        result = await session.execute(
            insert(Subscription)
            .values(user_id=user_id, group_id=group_id)
            .on_conflict_do_nothing()
        )
        await session.commit()
        return "added" if result.rowcount else "exists"

async def delete_user_subscription_db(telegram_id: int, queue: str, provider: str):
    async with session_factory() as session:
        result = await session.execute(
            delete(Subscription).where(
                Subscription.user_id == select(User.id).where(User.telegram_id == telegram_id).scalar_subquery(),
                Subscription.group_id == select(OutageGroup.id).where(
                    OutageGroup.provider == provider,
                    OutageGroup.queue == queue,
                ).scalar_subquery(),
            )
        )
        await session.commit()
        return bool(result.rowcount)