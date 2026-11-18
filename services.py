import json
import hashlib

from datetime import datetime

from data.config import MESSAGE_HEADERS, KYIV_TZ, OUTAGE_STATUS
from crud import (add_user_db, get_user_groups_db, add_user_subs_db,
                  delete_user_subscription_db, delete_all_user_subscriptions_db, update_today_schedule_info_db,
                  get_data_for_notify_db, update_provider_metadata_db, get_providers_update_time_db)
from message_builder import build_groups_message, build_schedule_message, construct_full_message, construct_message_footer
from exceptions import UnknownGroupError
from yasno_parser import get_provider_schedule_from_api


def _calculate_schedule_data_hash(schedule_data: dict) -> str:
    json_str = json.dumps(schedule_data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(json_str.encode('utf-8')).hexdigest()

async def _data_fot_footer_service() -> dict[str, str]:
    provider_datetime = {}
    data = await get_providers_update_time_db()
    for provider in data:
        provider_datetime[provider.provider] = provider.schedule_updated_time

    print(provider_datetime)
    return provider_datetime

async def add_user_service(tg_id: int):
    user = await add_user_db(telegram_id=tg_id)
    return user

async def get_user_groups_list_service(tg_id: int) -> list:
    user_groups = await get_user_groups_db(tg_id)
    if not user_groups:
        return []
    return [f"{user_group.provider}-{user_group.queue}" for user_group in user_groups]

async def get_user_groups_message_service(tg_id: int) -> str | None:
    user_groups = await get_user_groups_db(tg_id)
    if not user_groups:
        return None
    message = await build_groups_message(user_groups, header=MESSAGE_HEADERS["subs_list"])
    return message

async def get_message_user_schedule_service(tg_id: int) -> str | None:
    body = ""
    user_groups = await get_user_groups_db(tg_id)
    if not user_groups:
        return None
    for user_group in user_groups:
        temp = await build_schedule_message(
            provider=user_group.provider,
            queue=user_group.queue,
            schedule_json=user_group.today_schedule_json
        )
        body += temp
    providers_datetime = await _data_fot_footer_service()
    footer = await construct_message_footer(dtek_datetime=providers_datetime["ДТЕК"], cek_datetime=providers_datetime["ЦЕК"])
    message = await construct_full_message(header=MESSAGE_HEADERS["actual_schedule"], body=body, footer=footer)
    return message

async def update_user_subscriptions_service(tg_id: int, groups_queue: list, provider: str) -> str | None:
    try:
        for queue in groups_queue:
            await add_user_subs_db(tg_id, queue, provider)
        return await get_user_groups_message_service(tg_id)

    except UnknownGroupError:
        return 'error'

async def delete_user_subscription_service(telegram_id: int, group: str):
    group_data = group.split("-") #GROUP DATA LIKE -> ['ЦЕК', '1.1'] ['provider', 'queue']
    provider = group_data[0]
    queue = group_data[1]
    response = await delete_user_subscription_db(telegram_id=telegram_id, queue=queue, provider=provider)
    return response

async def delete_all_user_subscriptions_service(telegram_id):
    db_resp = await delete_all_user_subscriptions_db(telegram_id)
    return db_resp

async def update_today_schedule_info_service(provider, data):
    update_package = []
    for queue, value in data.items():
        if not isinstance(value, dict):
            continue
        today = value.get("today").get("slots")
        if today is None:
            continue

        data_hash = _calculate_schedule_data_hash(today)
        temp = {
            "provider": provider,
            "queue": queue,
            "data_json" : today,
            "data_hash" : data_hash,
        }
        update_package.append(temp)

    return await update_today_schedule_info_db(update_package)

async def update_provider_metadata_service(provider_name, data):
    updated_on = data.get("1.1").get("updatedOn")
    updated_time = datetime.fromisoformat(updated_on)
    outage_status = data.get("1.1").get("today").get("status")
    if outage_status == OUTAGE_STATUS["emergency"]:
        await update_provider_metadata_db(provider_name, updated_time, is_emergency=True)
    else:
        await update_provider_metadata_db(provider_name, updated_time, is_emergency=False)


async def parsing_data_from_yasno_service(provider_name) -> list[dict]:
    data = await get_provider_schedule_from_api(provider_name)
    if data is None:
        raise Exception(f"Provider {provider_name} API error")
    await update_provider_metadata_service(provider_name=provider_name, data=data)
    queue_changed = await update_today_schedule_info_service(provider=provider_name, data=data)
    return queue_changed

async def get_full_data_for_notify_service(groups_list: list[dict]) -> dict:
    answer = {}
    actual_data = await get_data_for_notify_db(groups_list)
    providers_datetime = await get_providers_update_time_db()
    footer = await construct_message_footer(dtek_datetime=providers_datetime["ДТЕК"],
                                            cek_datetime=providers_datetime["ЦЕК"])

    for notify in actual_data:
        user_tg_id = str(notify["telegram_id"])
        message_body = await build_schedule_message(
            provider=notify["provider"],
            queue=notify["queue"],
            schedule_json=notify["today_schedule_json"]
        )
        temp = {
            "message": message_body,
            "new_hash": notify["today_schedule_hash"]
        }
        if user_tg_id in answer.keys():
            answer[user_tg_id]["message"] += message_body
        else:
            answer[user_tg_id] = temp
    for obj in answer:
        temp_body = answer[obj]["message"]
        answer[obj]["message"] = await construct_full_message(header=MESSAGE_HEADERS["changed_schedule"],body=temp_body,footer=footer)

    return answer


