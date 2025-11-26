from typing import List

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from .models import Project
from .kwork_parser import get_projects
from .db import project_exists, save_project, get_all_subscribers


async def fetch_new_projects() -> List[Project]:
    """Парсим Kwork и возвращаем только новые проекты (которых ещё нет в БД)."""
    projects = await get_projects()
    new_projects: List[Project] = []

    for p in projects:
        if not project_exists(p.project_id):
            save_project(p)
            new_projects.append(p)

    return new_projects


def build_project_message(project: Project) -> str:
    # Обрезаем описание, чтобы не улететь в лимит Telegram
    desc = project.description or ""
    if len(desc) > 700:
        desc = desc[:700] + "…"

    return (
        f"<b>Новый проект на Kwork</b>\n\n"
        f"<b>{project.title}</b>\n"
        f"💰 {project.price}\n\n"
        f"{desc}\n\n"
        f"<a href=\"{project.url}\">Открыть проект</a>"
    )

def build_project_keyboard(project: Project) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔔 Откликнуться",
                callback_data=f"respond:{project.project_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🌐 Открыть на Kwork",
                url=project.url
            )
        ]
    ])
    return kb


async def broadcast_new_projects(bot: Bot) -> int:
    """
    Находит новые проекты, сохраняет их и рассылает всем подписчикам.
    Возвращает количество новых проектов.
    """
    new_projects = await fetch_new_projects()
    if not new_projects:
        return 0

    subscribers = get_all_subscribers()
    if not subscribers:
        return 0

    for project in new_projects:
        text = build_project_message(project)      # <-- ТЕПЕРЬ ТУТ СООБЩЕНИЕ
        kb = build_project_keyboard(project)

        for chat_id in subscribers:
            try:
                await bot.send_message(
                    chat_id,
                    text,
                    reply_markup=kb,
                    disable_web_page_preview=True
                )
            except Exception as e:
                print(f"Не удалось отправить сообщение {chat_id}: {e}")

    return len(new_projects)
