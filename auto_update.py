from storage import get_all_users
from data.config import GROUPS
from message_builder import builder_for_notification


def schedule_redactor(obj):
    #print(obj.get(f"{group}", {}).get("today", {}).get("slots", []) for group in GROUPS)
    fin = {group: [slot for slot in obj.get(group, {}).get("today", {}).get("slots", []) if slot.get("type") != "NotPlanned"]
        for group in GROUPS}
    #print("fin1 ",  fin)
    return fin


def schedule_change(provider, last, actual):
    last_sched = schedule_redactor(last)
    #print(last_sched)
    actual_sched = schedule_redactor(actual)
    #print(actual_sched)
    result = {}
    for group in GROUPS:
        if last_sched.get(group) != actual_sched.get(group):
            result[f"{provider}-{group}"] = actual_sched.get(group)

    #print("result = ", result)
    return result


async def updates(provider, last_state, current_data):
    #print(provider, "\n", last_state, "\n", current_data)
    diff_schedule = schedule_change(provider, last_state, current_data)
    #print(diff_schedule)
    if diff_schedule:
        all_users = await get_all_users()
        notify_for_user = {
            user.id : [slot for slot in user.groups if f"{slot[0]}-{slot[1]}" in diff_schedule] for user in all_users
        }
        #print(notify_for_user)

        return builder_for_notification(diff_schedule, notify_for_user,
                                        current_data.get("1.1", {}).get("today", {}).get("date", "No data")[:10].split("-"))
            #return diff_schedule
    else:
        return []