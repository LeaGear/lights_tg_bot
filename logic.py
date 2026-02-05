import requests
from storage import load, load_actual_schedule

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
    if sup == "ЦЕК":
        data = load_actual_schedule("cek.json")
    else:
        data = load_actual_schedule("dtek.json")

    my_schedule = data[group]["today"]["slots"]
    my_schedule1 = data[group]["tomorrow"]["slots"]
    graph = schedule_constructor(f"Постачальник: {sup}   Група: {group}\n",
                                 my_schedule, "Графік відключень на зараз: ")
    graph1 = schedule_constructor("", my_schedule1, "Графік відключень на завтра: ")
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