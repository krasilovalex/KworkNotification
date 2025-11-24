import os

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID  = int(os.getenv("ADMIN_ID", "0") or "0")

if not BOT_TOKEN:
    raise RuntimeError("Не найден BOT_TOKEN в .env - заполни файл .env")

DB_PATH = os.path.join(BASE_DIR, "kwork_bot.db")