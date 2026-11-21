from services import parsing_data_from_yasno_service, notify_updated_groups, emergency_outage_notification_service

async def parser_scheduler():
    dtek_changes = await parsing_data_from_yasno_service("ДТЕК")
    cek_changes = await parsing_data_from_yasno_service("ЦЕК")

    if dtek_changes.get("is_emergency_on") or cek_changes.get("is_emergency_on"):
        await emergency_outage_notification_service()

    else:
        updated_groups = dtek_changes.get("queue_changed", []) + cek_changes.get("queue_changed", [])
        if not updated_groups:
            return
        await notify_updated_groups(updated_groups)
