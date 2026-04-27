import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from .config import BOT_TOKEN
from .handlers import router
from .db import init_db
from .kwork_service import broadcast_new_projects
import traceback


POLL_INTERVAL = 60  # секунды между проверками Kwork (можешь потом увеличить до 120–180)


async def poll_kwork(bot: Bot):
    """Фоновая задача: периодически проверяет Kwork на новые проекты."""
    await asyncio.sleep(3)  # небольшая пауза после старта бота
    print("🔁 Фоновый мониторинг Kwork запущен")

    while True:
        try:
            count = await broadcast_new_projects(bot)
            if count > 0:
                print(f"📬 Найдено и разослано новых проектов: {count}")
            else:
                print("😴 Новых проектов нет")
        except Exception as e:
            # repr(e) покажет тип ошибки (даже если текст пустой)
            print(f"Ошибка при проверке Kwork: {repr(e)}")
            # Эта команда выведет весь путь ошибки (красный текст), как в прошлый раз
            traceback.print_exc()

        await asyncio.sleep(POLL_INTERVAL)


async def main():
    init_db()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()
    dp.include_router(router)

    # запускаем фоновый таск
    asyncio.create_task(poll_kwork(bot))

    print("🚀 Бот запущен. Нажми Ctrl+C для остановки.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
