
from crud import add_user_db, get_user_groups_db

async def add_user_service(tg_id):
    user = await add_user_db(telegram_id=tg_id)
    return user

async def get_user_groups_list_service(tg_id):
    user_groups = await get_user_groups_db(tg_id)
    if not user_groups:
        return
    message = await build_groups_message(user_groups)
    return