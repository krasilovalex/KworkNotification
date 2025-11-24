# app/kwork_parser.py

import aiohttp
from typing import List

from .models import Project

# Берём из репозитория
KWORK_URL = "https://kwork.ru/projects"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    # Если без авторизации ответ не приходит — позже добавим Cookie
}


async def get_projects(category_id: str = "11") -> List[Project]:
    """
    Парсим Kwork через их реальный POST API
    Возвращаем список Project
    """

    form = aiohttp.FormData()
    form.add_field("c", category_id)  # категория - программирование
    form.add_field("page", "1")

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.post(KWORK_URL, data=form, timeout=10) as response:
            response.raise_for_status()
            data = await response.json()

    wants: list[dict] = data["data"]["wants"]

    projects: List[Project] = []

    for want in wants:
        project_id = str(want["id"])
        title = want.get("name") or f"Проект #{project_id}"
        price = want.get("priceLimit") or "—"

        url = f"https://kwork.ru/projects/{project_id}"

        projects.append(Project(
            project_id=project_id,
            title=title,
            price=str(price),
            url=url
        ))

    print(f"[kwork_parser] Найдено проектов: {len(projects)}")
    return projects
