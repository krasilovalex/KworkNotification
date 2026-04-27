import os

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID  = int(os.getenv("ADMIN_ID", "0") or "0")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

LLM_MODEL = "openai/gpt-oss-20b:free"

if not BOT_TOKEN:
    raise RuntimeError("Не найден BOT_TOKEN в .env - заполни файл .env")

DB_PATH = os.path.join(BASE_DIR, "kwork_bot.db")

# Слова, ради которых мы вообще рассматриваем заказ
TARGET_KEYWORDS = [
    # База бэкенда
    "python", "golang", "fastapi", "postgresql", "docker", "бэкенд",
    # Инфраструктура
    "kafka", "redis", "kubernetes", "ci/cd", "linux", "nginx", "rest api", "asyncio",
    # Боты и скрипты
    "telegram", "бот", "парс", "скрипт", "api", "тг", "tg", "bot",
    # Сайты и фронтенд
    "сайт", "лендинг", "верстка", "html", "css", "фронтенд", "frontend",
    "react", "vue", "веб-сайт", "website", "landing", "под ключ",
    "wordpress", "tilda", "тильда", "битрикс", "bitrix",
    # === НОВОЕ: КРУПНЫЕ ВЕБ-ПРОЕКТЫ ===
    "платформа", "crm", "erp", "портал", "веб-приложение", "web app", "saas", "сервис",
    "приложение", "app", "ios", "android", "мобильное"
]

# Стоп-слова. Если хоть одно есть в заказе — сразу отбраковываем, даже если бюджет 1 000 000
STOP_WORDS = [
    # Учеба
    "курсовая", "дипломная", "лабораторная", "студент", "практика", "домашнее задание",
    # Офис
    "vba", "макрос", "макросы",
    # Сомнительное
    "накрутка"
]

MIN_BUDGET = 0