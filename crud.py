from sqlalchemy import select, delete, update, tuple_
from sqlalchemy.dialects.postgresql import insert
from database import session_factory, User, OutageGroup, Subscription, ProviderMetaData
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
            .join(ProviderMetaData, OutageGroup.provider == ProviderMetaData.provider)
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

async def delete_all_user_subscriptions_db(telegram_id: int):
    async with session_factory() as session:
        result = await session.execute(
            delete(Subscription).where(
                Subscription.user_id == select(User.id).where(User.telegram_id == telegram_id).scalar_subquery()
            )
        )
        await session.commit()
        return bool(result.rowcount)

# PARSER INTERACTIONS WITH DB

async def update_today_schedule_info_db(package: list[dict]) -> list[dict]:
    changed = []
    async with session_factory() as session:
        for items in package:
            group = await session.scalar(
                select(OutageGroup).where(
                    OutageGroup.provider == items["provider"],
                    OutageGroup.queue == items["queue"],
                )
            )
            if group is None:
                group = OutageGroup(provider=items["provider"], queue=items["queue"])
                session.add(group)

            if group.today_schedule_hash != items["data_hash"]:
                group.today_schedule_json = items["data_json"]
                group.today_schedule_hash = items["data_hash"]
                changed.append({
                    "provider": items["provider"],
                    "queue": items["queue"]
                })

        await session.commit()
        return changed

async def update_provider_metadata_db(provider_name, updated_on, is_emergency) -> bool:
    async with session_factory() as session:
        provider = await session.scalar(select(ProviderMetaData).where(ProviderMetaData.provider == provider_name))
        old_emergency_value = provider.is_emergency_shutdown

        provider.is_emergency_shutdown = is_emergency
        provider.schedule_updated_time = updated_on
        await session.commit()

        return old_emergency_value

async def get_data_for_notify_db(groups_list: list[dict]) -> list[dict]:
    pairs = [(g["provider"], g["queue"]) for g in groups_list]

    async with session_factory() as session:
        rows = await session.execute(
            select(
                User.telegram_id,
                Subscription.user_id,
                Subscription.group_id,
                OutageGroup.provider,
                OutageGroup.queue,
                OutageGroup.today_schedule_json,
                OutageGroup.today_schedule_hash,
            )
            .select_from(OutageGroup)
            .join(Subscription, Subscription.group_id == OutageGroup.id)
            .join(User, User.id == Subscription.user_id)
            .where(
                tuple_(OutageGroup.provider, OutageGroup.queue).in_(pairs),
                Subscription.last_notified_hash.is_distinct_from(OutageGroup.today_schedule_hash)
            )
        )
    return [dict(r._mapping) for r in rows]

async def get_providers_update_time_db() -> dict[str, str]:
    async with session_factory() as session:
        rows = await session.execute(select(ProviderMetaData.provider, ProviderMetaData.schedule_updated_time))
        return {provider : updated_at for provider, updated_at in rows}

async def get_users_tg_id_list_db() -> list[int]:
    async with session_factory() as session:
        rows = await session.scalars(select(User.telegram_id).distinct())
        return list(rows.all())

async def update_users_last_notify_hash_db(notified_users):
    async with session_factory() as session:

        for user_updated_groups_list in notified_users:
            for subs in user_updated_groups_list:
                await session.execute(
                    update(Subscription)
                    .where(Subscription.user_id == subs["user_id"],
                           Subscription.group_id == subs["group_id"])
                    .values(last_notified_hash=subs["new_hash"])
                )
        await session.commit()