# app/kwork_parser.py

import asyncio
from typing import List, Union

import aiohttp
from bs4 import BeautifulSoup

from .models import Project

# Эндпоинт списка проектов
KWORK_URL = "https://kwork.ru/projects"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    # Если понадобится, сюда можно добавить Cookie из браузера:
    # "Cookie": "kworkuid=...; PHPSESSID=...; ...",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
}


async def fetch_description(session: aiohttp.ClientSession, project_id: str) -> str:
    """
    Загружает страницу проекта и вытаскивает текст описания.
    Если не смогли — возвращаем пустую строку.
    """
    url = f"https://kwork.ru/projects/{project_id}"

    try:
        async with session.get(url, timeout=10) as resp:
            resp.raise_for_status()
            html = await resp.text()
    except Exception as e:
        print(f"[kwork_parser] Не удалось загрузить описание {project_id}: {e}")
        return ""

    soup = BeautifulSoup(html, "lxml")

    # Пробуем несколько вариантов блоков с описанием
    block = (
        soup.select_one(".card__content.js-description-text")
        or soup.select_one(".wants-card__text")
        or soup.select_one(".wants-card__description")
        or soup.find("div", {"itemprop": "description"})
        or soup.find("div", class_="description")
    )

    if not block:
        print(f"[kwork_parser] Описание не найдено для проекта {project_id}")
        return ""

    text = " ".join(block.get_text(separator=" ").split())
    print(f"[kwork_parser] Описание найдено для {project_id}: {text[:100]}...")
    return text


async def get_projects(category_id: str = "11") -> List[Project]:
    """
    Парсим Kwork через их реальный POST API
    и подтягиваем описание проекта:
      1) сначала пытаемся взять из JSON (want["description"]/["desc"]);
      2) если нет — грузим страницу проекта и парсим HTML.
    """
    projects: List[Project] = []

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        # 1) тянем список заказов (wants)
        form = aiohttp.FormData()
        form.add_field("c", category_id)  # категория - программирование
        form.add_field("page", "1")

        async with session.post(KWORK_URL, data=form, timeout=10) as response:
            response.raise_for_status()
            data = await response.json()

        wants: list[dict] = data["data"]["wants"]

        tasks: list[asyncio.Future] = []
        ids: list[str] = []
        raw_descs: list[Union[str, None]] = []

        # 2) сначала собираем ВСЕ возможные описания из JSON
        for want in wants:
            project_id = str(want["id"])
            ids.append(project_id)

            # разные возможные ключи, на всякий случай
            json_desc = (
                want.get("description")
                or want.get("desc")
                or want.get("shortDescription")
                or want.get("short_description")
            )

            raw_descs.append(json_desc)

            # HTML будем парсить ТОЛЬКО если в JSON ничего нет
            if json_desc:
                tasks.append(asyncio.sleep(0))  # заглушка, чтобы zip не ломался
            else:
                tasks.append(fetch_description(session, project_id))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 3) собираем Project с описанием
        for want, project_id, json_desc, fetched in zip(
            wants, ids, raw_descs, results
        ):
            title = want.get("name") or f"Проект #{project_id}"
            price = want.get("priceLimit") or "—"
            url = f"https://kwork.ru/projects/{project_id}"

            # приоритет — описание из JSON
            desc_text: str = ""
            if isinstance(json_desc, str) and json_desc.strip():
                desc_text = " ".join(json_desc.split())
            else:
                # если JSON-поля не было, используем результат HTML-парсинга
                if isinstance(fetched, Exception):
                    desc_text = ""
                elif isinstance(fetched, str):
                    desc_text = fetched
                else:
                    desc_text = ""

            projects.append(
                Project(
                    project_id=project_id,
                    title=str(title),
                    price=str(price),
                    url=url,
                    description=desc_text,
                )
            )

    print(f"[kwork_parser] Найдено проектов: {len(projects)}")
    return projects
