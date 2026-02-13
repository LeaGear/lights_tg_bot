import requests
from datetime import datetime
from sqlalchemy import select

from storage import load, save
from database import session_factory, User

def schedule_constructor(frst_msg, schedule, message):
    good_graph = (f"{frst_msg}\n"
                  f"{message}\n")
    for date in schedule:
        if date["type"] == 'Definite':
            start = int(date["start"])
            end = int(date["end"])
            temp = (f"⚡{'0'if (start/60) < 10 else''}{int(start/60)}{':00'if start % 60 == 0 else':30' } - "
                    f"{'0'if (end/60) < 10 else''}{int(end/60)}{':00'if end % 60 == 0 else':30' }\n")
            good_graph += temp
    #print(good_graph)
    return good_graph

def get_yasno_data(groups_list):
    end_version = ""
    for i in groups_list:
        sup = i[0]
        group = i[1]
        if sup == "ЦЕК":
            data = load("data/cek.json")
        else:
            data = load("data/dtek.json")

        my_schedule = data[group]["today"]["slots"]
        my_schedule1 = data[group]["tomorrow"]["slots"]
        graph = schedule_constructor(f"💡Постачальник: {sup}   Група: {group}💡\n",
                                     my_schedule, "Графік відключень на зараз: ")
        if my_schedule1:
            graph1 = schedule_constructor("", my_schedule1,
                                          f"Попередній графік відключень на завтра: ")
        else:
            graph1 = "\nНемає попереднього графіку на завтра!\n"
        all_graph = "\n" + "═"*20 + "\n" + graph + graph1 + "═"*20 + "\n"
        end_version += all_graph
        #print(end_version)
    time = data["1.1"]["today"]["date"][:10].split("-")
    last  = (f"\n\n❇️Дата актуальності графіка: {time[2]}/{time[1]}/{time[0]}\n\n"
             f"🔔Дата сповіщення: {str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))[:19]}")
    end_version += last
    return end_version




async def get_info(user_id):
    async with session_factory() as session:
        result = await session.execute(select(User).where(User.id == str(user_id)))
        user = result.scalar_one_or_none()

    if not user:
        return "Ви ще не обрали групу."

    if user.last_status == "EmergencyShutdowns":
        header = "🚨 ЕКСТРЕНІ ВІДКЛЮЧЕННЯ 🚨\nГрафіки не діють!\nОстанній актуальний графік:\n\n"
        results = header + get_yasno_data(user.groups)
        return results
    else:
        header = "️⚡⚡️Ось твій графік!⚡️⚡️\n"
        # user.groups — это уже готовый список!
        results = header + get_yasno_data(user.groups)
        return results

def get_from_api(provider, file_name):

    url = "https://app.yasno.ua/api/blackout-service/public/shutdowns/regions/3/dsos/" + str(provider) + "/planned-outages"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data["1.1"]["today"]["status"] == "EmergencyShutdowns":
            print("EmergencyShutdowns")
            return data
        # print(data)
        else:
            save(data, file_name)
            # print(data)
            print(f"{'CEK' if provider == 301 else 'DTEK'} schedule saved successfully!")
            return data
    else:
        return load(file_name)


