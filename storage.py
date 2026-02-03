import json

def load():
    all_data = []
    try:
        with open("data.json", "r", encoding="utf-8") as file1:
            all_data = json.load(file1)
    except FileNotFoundError:
        print("Create new file!")
    return all_data

def save(all_data):
    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(all_data, file, ensure_ascii=False, indent=2)
    print("Operation saved successfully!")
    print(all_data)

def users_table(data):
    all_data = load()
    print(data)
    id_list = []

    for user in all_data:
        id_list.append(user["id"])

    if data["id"] in id_list:
        del_rec = id_list.index(data["id"])
        all_data.pop(del_rec)
        all_data.append(data)
    else:
        all_data.append(data)
    save(all_data)