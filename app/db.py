import sqlite3
from contextlib import closing
from typing import List, Optional

from .config import DB_PATH
from .models import Project


def init_db():
    """Создаём таблицы, если их ещё нет."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()

        # Подписчики
        cur.execute("""
            CREATE TABLE IF NOT EXISTS subscribers (
                chat_id INTEGER PRIMARY KEY,
                is_active INTEGER DEFAULT 1
            )
        """)

        # Проекты
        cur.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                project_id TEXT PRIMARY KEY,
                title TEXT,
                price TEXT,
                url TEXT
            )
        """)

        conn.commit()


# ---------- подписчики ----------

def add_subscriber(chat_id: int):
    """Добавляем подписчика или активируем, если он уже есть."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO subscribers (chat_id, is_active)
            VALUES (?, 1)
        """, (chat_id,))
        conn.commit()


def get_subscribers_count() -> int:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM subscribers WHERE is_active = 1")
        row = cur.fetchone()
    return row[0] if row else 0


def get_all_subscribers() -> List[int]:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute("SELECT chat_id FROM subscribers WHERE is_active = 1")
        rows = cur.fetchall()
    return [r[0] for r in rows]


# ---------- проекты ----------

def project_exists(project_id: str) -> bool:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM projects WHERE project_id = ?", (project_id,))
        return cur.fetchone() is not None


def save_project(project: Project):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT OR IGNORE INTO projects (project_id, title, price, url)
            VALUES (?, ?, ?, ?)
        """, (
            project.project_id,
            project.title,
            project.price,
            project.url
        ))
        conn.commit()


def get_project_by_id(project_id: str) -> Optional[Project]:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT project_id, title, price, url
            FROM projects
            WHERE project_id = ?
        """, (project_id,))
        row = cur.fetchone()
    if not row:
        return None
    return Project(*row)
