from datetime import datetime
from data.config import KYIV_TZ

def time_zone_builder(start, end):
    zone = (f"⚡ з {'0'if (start/60) < 10 else''}{int(start/60)}{':00'if start % 60 == 0 else':30' } до "
                    f"{'0'if (end/60) < 10 else''}{int(end/60)}{':00'if end % 60 == 0 else':30' }\n")
    return zone

def get_actual_time(time):

    if time[0] == "No Data":
        return (f"\n\n❇️Дата актуальності графіка: НЕМАЄ ДАНИХ\n\n"
                 f"🔔Дата сповіщення: {str(datetime.now(KYIV_TZ).strftime("%d.%m.%Y %H:%M:%S"))[:19]}")
    else:
        return (f"\n\n❇️Дата актуальності графіка: {time[2]}.{time[1]}.{time[0]}\n\n"
                f"🔔Дата сповіщення: {str(datetime.now(KYIV_TZ).strftime("%d.%m.%Y %H:%M:%S"))[:19]}")


def schedule_constructor(frst_msg, schedule, message, reserve):
    temp = ""

    for date in schedule:
        if date["type"] == 'Definite':
            start = int(date["start"])
            end = int(date["end"])
            temp += time_zone_builder(start, end)

    if temp:
        finish_alert = (f"{frst_msg}\n"
                      f"{message}\n")
        finish_alert += temp
    else:
        finish_alert = (f"{frst_msg}\n"
                        f"{reserve}\n")

    return finish_alert


def builder_for_notification(sched_ch, users, date):
    final_list = []
    header = ("❗❗УВАГА❗❗\n"
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
                    message += time_zone_builder(start, end)

            message += get_actual_time(date)
            final_list.append([user_id, message])

    return final_list