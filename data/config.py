import os
import pytz

from dotenv import load_dotenv

load_dotenv("data/.env")

TOKEN = os.getenv("TOKEN")
DB_URL = os.getenv("DB_PSQL_URL")
API_URL = "https://app.yasno.ua/api/blackout-service/public/shutdowns/regions/3/dsos/{code}/planned-outages"

PROVIDERS_CODE = {
    "ЦЕК":  "303",
    "ДТЕК": "301"
}

MESSAGE_HEADERS = {
    "actual_schedule" : "️⚡️⚡️Графік за твоїми підписками!⚡️⚡️\n\n\n",
    "changed_schedule" : "❗❗УВАГА ГРАФІК ЗМІНИВСЯ!❗❗\n\n",
    "subs_list" : "📜Ось список груп за якими ти слідкуєш!📜\n"

}

MESSAGE_TEMPLATES = {
    "emergency_outage" : "🚨 ЗАПРОВАДЖЕНІ ЕКСТРЕНІ ВІДКЛЮЧЕННЯ 🚨\nГрафіки не діють!"
}

OUTAGE_STATUS = {
    "regular" : "ScheduleApplies",
    "emergency" : "EmergencyShutdowns",
    "waiting" : "WaitingForSchedule"
}

GROUPS = ["1.1", "1.2", "2.1", "2.2", "3.1", "3.2", "4.1", "4.2", "5.1", "5.2", "6.1", "6.2"]
KYIV_TZ = pytz.timezone('Europe/Kyiv')

USERS_UPDATED_COUNT = 25

RATE_LIMIT = 0.05
PARSER_REFRESH_INTERVAL_IN_MINUTES = 1 #minutes
REFRESH_INTERVAL_ALERT = 1 #minute