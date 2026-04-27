from aiogram import Router, F, types, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from .db import add_subscriber, get_subscribers_count, get_project_by_id
from .kwork_service import broadcast_new_projects
from .kwork_parser import get_projects
from .config import ADMIN_ID
from html import escape
from .llm_service import generate_reply


router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    add_subscriber(message.chat.id)

    total = get_subscribers_count()
    await message.answer(
        "Привет! 👋\n\n"
        "Я слежу за новыми заказами по разработке на Kwork и буду слать их сюда.\n\n"
        f"Сейчас на рассылку подписано: <b>{total}</b> пользователь(а).\n\n"
    )


@router.message(Command("test_kwork"))
async def cmd_test_kwork(message: Message):
    await message.answer("🔍 Проверяю Kwork на новые проекты...")

    count = await broadcast_new_projects(message.bot)

    if count == 0:
        await message.answer("Пока новых проектов нет 👀")
    else:
        await message.answer(f"Отправил <b>{count}</b> новых проектов всем подписчикам✅")


@router.callback_query(F.data.startswith("respond:"))
async def on_respond(callback: CallbackQuery, bot: Bot):
    project_id = callback.data.split(":", 1)[1]
    project = get_project_by_id(project_id)

    if not project:
        await callback.answer("Проект не найден 🤔", show_alert=True)
        return

    # Формируем mention пользователя
    if callback.from_user:
        u = callback.from_user
        name = u.full_name or u.username or "Пользователь"
        user_mention = f'<a href="tg://user?id={u.id}">{escape(name)}</a>'
    else:
        user_mention = "неизвестный пользователь"

    text = (
        "📨 <b>Новый отклик на проект</b>\n\n"
        f"От: {user_mention}\n"
        f"Проект: <b>{project.title}</b>\n"
        f"💰 {project.price}\n"
        f"{project.url}"
    )

    # Шлём админу
    try:
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=text,
            disable_web_page_preview=True,
        )
    except Exception as e:
        print(f"Не удалось отправить отклик админу: {e}")

    # Ответ юзеру
    await callback.answer("Я передал ваш отклик админу 👌", show_alert=True)

from .kwork_parser import get_projects


@router.message(Command("probe"))
async def cmd_probe(message: Message):
    await message.answer("🔍 Пробую спарсить хотя бы 1 проект с Kwork...")

    projects = await get_projects()

    if not projects:
        await message.answer("❌ Парсер ничего не нашёл. Скорее всего, надо править селекторы.")
        return

    p = projects[0]  # первый найденный проект

    text = (
        f"✅ <b>Парсинг работает</b>\n\n"
        f"<b>{p.title}</b>\n"
        f"💰 {p.price}\n"
        f"{p.url}"
    )

    await message.answer(text, disable_web_page_preview=True)


@router.callback_query(F.data.startswith("gen_"))
async def on_generate_cover_letter(callback: CallbackQuery):
    project_id = callback.data.split(":", 1)[1]
    project = get_project_by_id(project_id)

    if not project:
        await callback.answer("Проект не найден в БД", show_alert=True)
        return
    
    await callback.answer("⏳ Нейросеть генерирует отклик, подожди...", show_alert=False)

    cover_letter = await generate_cover_letter(project.title, project.description)


    text = (
        f"🤖 <b>Сгенерированный отклик</b>\n"
        f"Проект: {project.title}\n\n"
        f"<code>{escape(cover_letter)}</code>\n\n"
        f"<i>(Нажми на текст отклика, чтобы скопировать его)</i>"
    )


    await callback.message.answer(text, parse_mode="HTML")
