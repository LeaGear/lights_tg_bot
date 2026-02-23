import httpx
from sqlalchemy import select

from data.config import PROVIDERS
from storage import load
from database import session_factory, User
from message_builder import schedule_constructor, get_actual_time

async def get_yasno_data(groups_list, data_cek = None, data_dtek = None):

    if data_cek is None: data_cek = await load(PROVIDERS["CEK"]["file"])
    if data_dtek is None: data_dtek = await load(PROVIDERS["DTEK"]["file"])
    end_version = ""
    for i in groups_list:
        sup = i[0]
        group = i[1]
        # Используем переданные словари
        data = data_cek if sup == "ЦЕК" else data_dtek

        my_schedule_today = data.get(group, {}).get("today", {}).get("slots", [])
        my_schedule_tomorrow = data.get(group, {}).get("tomorrow", {}).get("slots", [])

        graph_today = schedule_constructor(f"💡Постачальник: {sup}   Група: {group}💡\n",
                                     my_schedule_today, "Графік відключень на cьогодні: ",
                                           "\nНа даний момент відключення відсутні!\n")

        graph_tomorrow = schedule_constructor("", my_schedule_tomorrow,
                                      f"Попередній графік відключень на завтра: ",
                                              "\nНемає попереднього графіку на завтра!\n")

        all_graph = "\n" + "═"*20 + "\n" + graph_today + graph_tomorrow + "═"*20 + "\n"
        end_version += all_graph
        #print(end_version)
    time = data.get("1.1", {}).get("today", {}).get("date", "No data")[:10].split("-")
    #print(time)
    end_version += get_actual_time(time)
    return end_version




async def get_info(user_id):
    sched_cek = await load(PROVIDERS["CEK"]["file"])
    sched_dtek = await load(PROVIDERS["DTEK"]["file"])
    async with session_factory() as session:
        result = await session.execute(select(User).where(User.id == str(user_id)))
        user = result.scalar_one_or_none()

    if not user or not user.groups:
        return "🟡 Ти не обрав жодної групи 🟡"

    if user.last_status == "EmergencyShutdowns":
        header = "🚨 ЕКСТРЕНІ ВІДКЛЮЧЕННЯ 🚨\nГрафіки не діють!\nОстанній актуальний графік:\n"
        results = header + await get_yasno_data(user.groups, sched_cek, sched_dtek)
        return results
    else:
        header = "️⚡⚡️Ось твій графік!⚡️⚡️\n"
        results = header + await get_yasno_data(user.groups, sched_cek, sched_dtek)
        return results

async def get_from_api(provider, file_name):

    url = "https://app.yasno.ua/api/blackout-service/public/shutdowns/regions/3/dsos/" + str(provider) + "/planned-outages"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return load(file_name)


