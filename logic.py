import requests
from storage import load

def schedule_constructor(frst_msg, schedule, message):
    good_graph = (f"{frst_msg}\n"
                  f"{message}\n")
    for date in schedule:
        if date["type"] == 'Definite':
            temp = (f"⚡{int(date['start']/60)}{':00'if date['start'] % 60 == 0 else':30' } - "
                    f"{int(date['end']/60)}{':00'if date['end'] % 60 == 0 else':30' }\n")
            good_graph += temp
    #print(good_graph)
    return good_graph

def get_yasno_data(sup, group):
    if sup == "ЦЕК":
        sup_dig = 303
    else:
        sup_dig = 301


    url = "https://app.yasno.ua/api/blackout-service/public/shutdowns/regions/3/dsos/" + str(sup_dig) + "/planned-outages"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
    else:
        pass
    my_schedule = data[group]["today"]["slots"]
    my_schedule1 = data[group]["tomorrow"]["slots"]
    #print(my_schedule)
    #good_graph = (f"Поставщик: {sup}   Группа: {group}\n")
    graph = schedule_constructor(f"Поставщик: {sup}   Группа: {group}\n",
                                 my_schedule, "График на данный момент: ")
    graph1 = schedule_constructor("\n", my_schedule1, "А это график на завтра: ")
    all_graph = graph + graph1
    #print(all_graph)
    return all_graph

def get_info(user):
    #print(user)
    user_list = load()
    #print(user_list)
    user_dict = next((item for item in user_list if item["id"] == str(user)), None)
    #print(user_dict)
    graph = get_yasno_data(user_dict["sup"], user_dict["group"])
    return graph

def get_yasno(sup):
    if sup == "ЦЕК":
        sup_dig = 303
    else:
        sup_dig = 301

    url = "https://app.yasno.ua/api/blackout-service/public/shutdowns/regions/3/dsos/" + str(
        sup_dig) + "/planned-outages"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
    else:
        pass

    return data