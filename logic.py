import requests
from storage import load, save
from database import Session, User

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

def get_yasno_data(sup, group):
    end_version = ""
    if sup == "ЦЕК":
        data = load("data/cek.json")
    else:
        data = load("data/dtek.json")

    for i in group:
        my_schedule = data[i]["today"]["slots"]
        my_schedule1 = data[i]["tomorrow"]["slots"]
        graph = schedule_constructor(f"Постачальник: {sup}   Група: {i}\n",
                                     my_schedule, "Графік відключень на зараз: ")
        if my_schedule1:
            graph1 = schedule_constructor("", my_schedule1,
                                          f"Попередній графік відключень на завтра: ")
        else:
            graph1 = "\nНемає попереднього графіку на завтра!\n"
        all_graph = graph + graph1 + "═"*20 + "\n"
        end_version += all_graph
    #print(end_version)
    last  = f"\n\n🔔Дата оновлення: {data["1.1"]["today"]["date"][:10]}"
    end_version += last

    return end_version

def get_info(user_id):
    session = Session()
    user = session.query(User).filter_by(id=str(user_id)).first()
    #print(user.sup, user.group)
    session.close()

    if not user:
        return "Ви ще не обрали групу."

    if user.last_status == "EmergencyShutdowns":
        header = "🚨 ЕКСТРЕНІ ВІДКЛЮЧЕННЯ 🚨\nГрафіки не діють!\nОстанній актуальний графік:\n\n"
        results = header + get_yasno_data(user.sup, user.groups)
        return results
    else:
        header = "️⚡⚡️Ось твій графік!⚡️⚡️\n"
        # user.groups — это уже готовый список!
        results = header + get_yasno_data(user.sup, user.groups)
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


