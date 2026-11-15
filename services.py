from data.config import LOCALIZATION

from crud import add_user_db, get_user_groups_db, add_user_subs_db, delete_user_subscription_db, delete_all_user_subscriptions_db
from message_builder import build_groups_message, build_schedule_message
from exceptions import UnknownGroupError

async def add_user_service(tg_id: int):
    user = await add_user_db(telegram_id=tg_id)
    return user

async def get_user_groups_list_service(tg_id: int) -> list:
    user_groups = await get_user_groups_db(tg_id)
    if not user_groups:
        return []
    else:
        result = []
        for user_group in user_groups:
            result.append(f"{LOCALIZATION.get(user_group.provider, "")}-{user_group.queue}")
        return result

async def get_user_groups_message_service(tg_id: int) -> str | None:
    user_groups = await get_user_groups_db(tg_id)
    if not user_groups:
        return None
    message = await build_groups_message(user_groups)
    return message

async def get_message_user_schedule_service(tg_id: int) -> str | None:
    user_groups = await get_user_groups_db(tg_id)
    if not user_groups:
        return None
    message = await build_schedule_message(user_groups)
    return message

async def update_user_subscriptions_service(tg_id: int, groups_queue: list, provider: str) -> str | None:
    try:
        for queue in groups_queue:
            await add_user_subs_db(tg_id, queue, LOCALIZATION.get(provider, ""))
        return await get_user_groups_message_service(tg_id)

    except UnknownGroupError:
        return 'error'

async def delete_user_subscription_service(telegram_id: int, group: str):
    group_data = group.split("-")
    provider = LOCALIZATION.get(group_data[0], "")
    queue = group_data[1]
    response = await delete_user_subscription_db(telegram_id=telegram_id, queue=queue, provider=provider)
    return response

async def delete_all_user_subscriptions_service(telegram_id):
    db_resp = await delete_all_user_subscriptions_db(telegram_id)
    return db_resp