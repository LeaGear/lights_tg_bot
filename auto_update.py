from storage import get_all_users
from datetime import datetime

from data.config import GROUPS, KYIV_TZ


def schedule_redactor(obj):
    fin = {group: [slot for slot in obj[group]["today"]["slots"] if slot.get("type") != "NotPlanned"]
        for group in GROUPS}
    #print("fin1 ",  fin)
    return fin


def schedule_change(provider, last, actual):
    red_last = schedule_redactor(last)
    red_actual = schedule_redactor(actual)
    result = {}
    for group in GROUPS:
        if red_last.get(group) != red_actual.get(group):
            result[f"{provider}-{group}"] = red_actual.get(group)

    #print("result = ", result)
    return result


def notify_constructor(sched_ch, users, date):
    final_list = []
    header = ("❗УВАГА❗ ❗УВАГА❗ ❗УВАГА!❗\n"
              "❗ГРАФІК НА СЬОГОДНІ ЗМІНИВСЯ!❗\n"
              "✔️Показано лише ті групи, за якими ви слідкуєте!✔️\n")
    for user_id, user_groups in users.items():
        if user_groups:
            message = header
            for gp in user_groups:
                message += "\n" + "═"*20 + f"\nПостачальник - {gp[0]} Група - {gp[1]}\n\n"
                temp = sched_ch[f"{gp[0]}-{gp[1]}"]
                for j in temp:
                    start = j.get("start")
                    end = j.get("end")
                    if start is None and end is None:
                        continue
                    tm = (f"⚡{'0' if (start / 60) < 10 else ''}{int(start / 60)}{':00' if start % 60 == 0 else ':30'} - "
                            f"{'0' if (end / 60) < 10 else ''}{int(end / 60)}{':00' if end % 60 == 0 else ':30'}\n")
                    message += tm

            last = ("\n" + "═"*20 + f"\n\n❇️Дата актуальності графіка: {date[2]}.{date[1]}.{date[0]}\n\n"
                    f"🔔Дата сповіщення: {str(datetime.now(KYIV_TZ).strftime("%d.%m.%Y %H:%M:%S"))[:19]}")
            message += last
            final_list.append([user_id, message])
        #print(message)
        #print(final_list)
    return final_list

async def update(provider, last_state, current_data):
    diff_schedule = schedule_change(provider, last_state, current_data)
    if diff_schedule:
        all_users = await get_all_users()
        notify_for_user = {
            user.id : [slot for slot in user.groups if f"{slot[0]}-{slot[1]}" in diff_schedule] for user in all_users
        }
        #print(notify_for_user)

        return notify_constructor(diff_schedule, notify_for_user, current_data["1.1"]["today"]["date"][:10].split("-"))
            #return diff_schedule
    else:
        return []