
from crud import add_user_db

async def add_user_service(tg_id):
    user = await add_user_db(telegram_id=tg_id)
    return user

