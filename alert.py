from datetime import datetime

from storage import load
from data.config import PROVIDERS, GROUPS, KYIV_TZ


def optimize_schedule_for_alert(schedule):
    simplified_list = {group:[slot.get("start") for slot in schedule[group]["today"]["slots"]
                              if slot.get("type") == "Definite"] for group in GROUPS}
    #print(simplified_list)
    return simplified_list

def constructor(provider, now, sch_list, alert_list):
    for group in GROUPS:
        for slot in sch_list[group]:
            if (slot - now) == 10: alert_list.append([provider, group])

    return alert_list

async def alert_groups_list():
    alert_list = []
    now = datetime.now(KYIV_TZ)
    # Считаем, сколько минут прошло с начала дня
    current_minutes_from_start_of_day = now.hour * 60 + now.minute

    simp_sched_dtek = optimize_schedule_for_alert(await load(PROVIDERS["DTEK"]["file"]))
    simp_sched_cek = optimize_schedule_for_alert(await load(PROVIDERS["CEK"]["file"]))

    alert_list = constructor("ЦЕК", current_minutes_from_start_of_day, simp_sched_cek, alert_list)
    alert_list = constructor("ДТЕК", current_minutes_from_start_of_day, simp_sched_dtek, alert_list)
    #print(alert_list)

    return alert_list
