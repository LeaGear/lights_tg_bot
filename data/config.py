import os
import pytz

from dotenv import load_dotenv

load_dotenv("data/.env")

TOKEN = os.getenv("TOKEN")
DB_URL = "sqlite+aiosqlite:///data/users.db"

PROVIDERS = {
    "CEK": {"code" : 303, "file" : "data/cek.json"},
    "DTEK": {"code" : 301, "file" : "data/dtek.json"},
}

GROUPS = ["1.1", "1.2", "2.1", "2.2", "3.1", "3.2", "4.1", "4.2", "5.1", "5.2", "6.1", "6.2"]
KYIV_TZ = pytz.timezone('Europe/Kyiv')
RATE_LIMIT = 0.05
REFRESH_INTERVAL = 5 #minutes
REFRESH_INTERVAL_ALERT = 1 #minute