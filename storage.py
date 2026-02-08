import json
from database import Session, User



def users_table(data):
    session = Session()
    uid = data["id"]
    user = session.query(User).filter(User.id == uid).first()

    if user:
        user.sup = data["sup"]
        user.groups = data["group"]
        user.notifications = data["notifications"]
    else:
        new_user = User(id=uid, sup=data["sup"], groups=data["group"], notifications=data["notifications"])
        session.add(new_user)

    session.commit()
    session.close()

def get_all_users():
    session = Session()
    users = session.query(User).all()
    session.close()
    return users


def load(file_name):
    all_data = []
    try:
        with open(file_name, "r", encoding="utf-8") as file1:
            all_data = json.load(file1)
    except FileNotFoundError:
        print("Create new file!")
    return all_data

def save(all_data, file_name):
    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(all_data, file, ensure_ascii=False, indent=2)
    print("Operation saved successfully!")
    #print(all_data)
