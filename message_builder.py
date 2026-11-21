from datetime import datetime
from data.config import KYIV_TZ



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
            temp += _time_zone_builder(start, end)

    if temp:
        finish_alert = (f"{frst_msg}\n"
                      f"{message}\n")
        finish_alert += temp
    else:
        finish_alert = (f"{frst_msg}\n"
                        f"{reserve}\n")

    return finish_alert


def builder_for_notification(sched_ch, users, date, header=""):
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
                    message += _time_zone_builder(start, end)

            message += get_actual_time(date)
            final_list.append([user_id, message])

    return final_list

# <<<<<<<<<<< NEW FUNCTION FOR UPDATED BOT >>>>>>>>>

def _json_schedule_parser(slots) -> str | None:
    print(slots)
    if slots is None:
        return "⚡ Наразі немає інформації про відключення ⚡\n"

    result = ""

    for slot in slots:
        if slot["type"] == "Definite":
            start = slot["start"]
            end = slot["end"]
            result += _time_zone_builder(start, end)
    if not result:
        return "⚡ Наразі немає інформації про відключення ⚡\n"

    return result

def _time_zone_builder(start, end):
    zone = (f"⚡ з {'0'if (start/60) < 10 else''}{int(start/60)}{':00'if start % 60 == 0 else':30' } до "
                    f"{'0'if (end/60) < 10 else''}{int(end/60)}{':00'if end % 60 == 0 else':30' }\n")
    return zone

async def build_groups_message(user_groups, header=""):
    result = ""
    result += header

    for group_data in user_groups:
        temp = f"{group_data.provider}-{group_data.queue}, "
        result += temp
    result = result[:-2]
    return result

async def build_schedule_body(provider, queue, schedule_json):
    message = (f"💡Група: {provider}-{queue}💡\n\n"
            #f"Графік відключень на сьогодні:\n"
                f"{_json_schedule_parser(schedule_json)}\n"
                )
    return message

async def construct_message_footer(dtek_datetime=None, cek_datetime=None) -> str:
    footer = ""
    if dtek_datetime is not None:
        footer += f"❇️Актуальність графіка ДТЕК: {dtek_datetime.strftime('%d.%m.%Y %H:%M')}\n"
    if cek_datetime is not None:
        footer += f"❇️Актуальність графіка ЦЕК: {cek_datetime.strftime('%d.%m.%Y %H:%M')}\n"
    return footer

async def construct_full_message(header="", body="", footer="") -> str:
    result = header + body + footer
    return result