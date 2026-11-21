import json
import hashlib

from datetime import datetime

from data.config import MESSAGE_HEADERS, OUTAGE_STATUS, MESSAGE_TEMPLATES, USERS_UPDATED_COUNT
from bot_instance import bot
from crud import (add_user_db, get_user_groups_db, add_user_subs_db,
                  delete_user_subscription_db, delete_all_user_subscriptions_db, update_today_schedule_info_db,
                  get_data_for_notify_db, update_provider_metadata_db, get_providers_update_time_db, get_users_tg_id_list_db,
                  update_users_last_notify_hash_db)
from message_builder import build_groups_message, build_schedule_body, construct_full_message, construct_message_footer
from exceptions import UnknownGroupError
from yasno_parser import get_provider_schedule_from_api


def _calculate_schedule_data_hash(schedule_data: dict) -> str:
    json_str = json.dumps(schedule_data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(json_str.encode('utf-8')).hexdigest()

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
        temp = await build_schedule_body(
            provider=user_group.provider,
            queue=user_group.queue,
            schedule_json=user_group.today_schedule_json
        )
        body += temp
    providers_datetime = await get_providers_update_time_db()
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

async def update_provider_metadata_service(provider_name, data) -> dict:
    updated_on = data.get("1.1").get("updatedOn")
    updated_time = datetime.fromisoformat(updated_on)
    outage_status = data.get("1.1").get("today").get("status")
    if outage_status == OUTAGE_STATUS["emergency"]:
        emergency_status = True
    else:
        emergency_status = False
    old_emergency_value = await update_provider_metadata_db(provider_name, updated_time, is_emergency=emergency_status)

    return {
        "is_emergency_on": (not old_emergency_value and emergency_status),
        "is_emergency_continue" : old_emergency_value and emergency_status
    }

async def parsing_data_from_yasno_service(provider_name) -> dict:
    data = await get_provider_schedule_from_api(provider_name)
    if data is None:
        raise Exception(f"Provider {provider_name} API error")

    provider_status = await update_provider_metadata_service(provider_name=provider_name, data=data)
    if provider_status.get("is_emergency_continue") or provider_status.get("is_emergency_on"):
        queue_changed = []
    else:
        queue_changed = await update_today_schedule_info_service(provider=provider_name, data=data)

    provider_status["queue_changed"] = queue_changed
    return provider_status

async def get_full_data_for_notify_service(groups_list: list[dict]) -> dict[int, dict]:
    answer = {}
    actual_data = await get_data_for_notify_db(groups_list)
    providers_datetime = await get_providers_update_time_db()
    footer = await construct_message_footer(dtek_datetime=providers_datetime["ДТЕК"],
                                            cek_datetime=providers_datetime["ЦЕК"])
    for notify in actual_data:
        user_tg_id = notify["telegram_id"]
        message_body = await build_schedule_body(
            provider=notify["provider"],
            queue=notify["queue"],
            schedule_json=notify["today_schedule_json"]
        )

        group_hash_pair = {
            "user_id" : notify["user_id"],
            "group_id": notify["group_id"],
            "new_hash" : notify["today_schedule_hash"]
        }

        if user_tg_id in answer.keys():
            answer[user_tg_id]["message"] += message_body
            answer[user_tg_id]["new_hash_data"].append(group_hash_pair)
        else:
            temp = {
                "message" : message_body,
                "new_hash_data" : [group_hash_pair]
            }
            answer[user_tg_id] = temp

    for entry in answer.values():
        entry["message"] = await construct_full_message(
            header=MESSAGE_HEADERS["changed_schedule"],
            body=entry["message"],
            footer=footer,
        )
    return answer

async def notify_updated_groups(groups_list: list[dict]):
    notified_users = [] # list[list[dict]]
    notify_list = await get_full_data_for_notify_service(groups_list)

    for tg_id ,value in notify_list.items():
        await bot.send_message(tg_id, value["message"])
        notified_users.append(value["new_hash_data"])
        if len(notified_users) == USERS_UPDATED_COUNT:
            await update_users_last_notify_hash_db(notified_users)
            notified_users = []

    if notified_users:
        await update_users_last_notify_hash_db(notified_users)

async def emergency_outage_notification_service():
    all_users = await get_users_tg_id_list_db()
    emergency_message = MESSAGE_TEMPLATES["emergency_outage"]
    for user_tg_id in all_users:
        try:
            bot.send_message(user_tg_id, emergency_message)
        except Exception as e:
            print(e)