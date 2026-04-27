import os

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID  = int(os.getenv("ADMIN_ID", "0") or "0")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

LLM_MODEL = "google/gemma-3-4b-it:free"

if not BOT_TOKEN:
    raise RuntimeError("Не найден BOT_TOKEN в .env - заполни файл .env")

DB_PATH = os.path.join(BASE_DIR, "kwork_bot.db")

# Слова, ради которых мы вообще рассматриваем заказ
TARGET_KEYWORDS = [
    # База
    "python", "golang", "fastapi", "postgresql", "docker", "бэкенд",
    # БД, кэши, брокеры
    "kafka", "redis", "clickhouse", "elasticsearch", "elastic", "mongodb", "celery",
    # Инфраструктура
    "kubernetes", "k8s", "ci/cd", "gitlab", "linux", "nginx", "terraform",
    # Фреймворки и спецификации
    "django", "drf", "grpc", "graphql", "sqlalchemy", "asyncio", "rest api",
    # Процессы и архитектура
    "highload", "хайлоад", "рефакторинг", "оптимизация", "интеграция", "saas", 
    "архитектура", "микросервис", "парсинг"
]

# Стоп-слова. Если хоть одно есть в заказе — сразу отбраковываем, даже если бюджет 1 000 000
STOP_WORDS = [
    # Учеба
    "курсовая", "дипломная", "лабораторная", "студент", "практика", "домашнее задание",
    # CMS и конструкторы
    "тильда", "tilda", "wordpress", "конструктор", "битрикс", "bitrix", "opencart",
    # Офис
    "эксель", "excel", "vba", "макрос", "макросы",
    # Сомнительное
    "накрутка", "отзывы"
]

MIN_BUDGET = 2000