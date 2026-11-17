from bot_instance import bot
from services import parsing_data_from_yasno_service, get_full_data_for_notify_service


async def _notify_updated_groups(groups_list: list[dict]):
    notified_users = {}
    notify_list = await get_full_data_for_notify_service(groups_list)
    for tg_id ,value in notify_list.items():
        await bot.send_message(tg_id, value["message"])
        notified_users[tg_id] = value["new_hash"]

    #update last_notified_hash

async def parser_scheduler():

    dtek_changed_groups = await parsing_data_from_yasno_service("ДТЕК")
    cek_changed_groups = await parsing_data_from_yasno_service("ЦЕК")
    updated_groups = dtek_changed_groups + cek_changed_groups
    if not updated_groups:
        return
    await _notify_updated_groups(updated_groups)
