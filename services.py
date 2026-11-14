
from crud import add_user_db, get_user_groups_db
from message_builder import build_groups_message, build_schedule_message

async def add_user_service(tg_id):
    user = await add_user_db(telegram_id=tg_id)
    return user

async def get_user_groups_list_service(tg_id) -> str | None:
    user_groups = await get_user_groups_db(tg_id)
    if not user_groups:
        return None
    message = await build_groups_message(user_groups)
    return message

async def get_user_schedule_service(tg_id) -> str | None:
    user_groups = await get_user_groups_db(tg_id)
    if not user_groups:
        return None
    message = await build_schedule_message(user_groups)
    return message