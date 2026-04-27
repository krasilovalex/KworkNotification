import json
import re
import aiohttp
from .config import OPENROUTER_API_KEY, LLM_MODEL  # Проверь правильность импорта своих настроек!

async def send_to_openrouter(system_prompt: str, user_prompt: str) -> str:
    """Вспомогательная функция для отправки HTTP-запросов к OpenRouter"""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": LLM_MODEL, 
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }
    
    try:
        # Коннектор с отключенным SSL (как мы настраивали ранее)
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=20) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    print(f"❌ Ошибка API: {resp.status}")
                    return ""
    except Exception as e:
        print(f"❌ Ошибка сети: {e}")
        return ""


async def generate_reply(title: str, description: str) -> str:
    """Двухступенчатый пайплайн: Анализатор -> Генератор"""
    
    # ==========================================
    # ЭТАП 1: АНАЛИЗАТОР (Техлид)
    # ==========================================
    analyzer_system = (
        "Ты суровый техлид. Проанализируй заказ и верни ТОЛЬКО валидный JSON без текста и форматирования.\n"
        "Формат:\n"
        "{\n"
        '  "optimal_stack": "Какие конкретно технологии нужны?",\n'
        '  "result_format": "В каком виде отдать результат? (Если просят скачать файлы/видео - пиши строго \'Сохранение на диск/архив\'. Если анализ данных - \'CSV/JSON\', Если сайт - \'Верстка/CMS\')",\n'
        '  "client_level": "Технарь или обычный бизнесмен?",\n'
        '  "core_task": "В чем главная суть задачи в 1 предложении?"\n'
        "}"
    )
    analyzer_user = f"Заголовок: {title}\nОписание: {description}"
    
    print(f"🤖 [Анализатор] Изучаю задачу: {title}")
    analyzer_response = await send_to_openrouter(analyzer_system, analyzer_user)
    
    # Пытаемся вытащить JSON из ответа (на случай, если ИИ добавил маркдаун ```json)
    analysis_data = {}
    try:
        json_match = re.search(r'\{.*\}', analyzer_response, re.DOTALL)
        if json_match:
            analysis_data = json.loads(json_match.group())
            print(f"✅ [Анализатор] Понял суть: {analysis_data.get('core_task')} | Формат: {analysis_data.get('result_format')}")
        else:
            raise ValueError("JSON не найден в ответе")
    except Exception as e:
        print(f"⚠️ [Анализатор] Ошибка парсинга JSON: {e}")
        # Фолбэк-заглушка, если ИИ сломался, чтобы бот не упал
        analysis_data = {
            "core_task": description[:100],
            "optimal_stack": "Инструменты под задачу",
            "result_format": "Удобный для клиента формат",
            "client_level": "Обычный пользователь"
        }
        
    # ==========================================
    # ЭТАП 2: ГЕНЕРАТОР (Копирайтер-переговорщик)
    # ==========================================
    generator_system = (
        "Ты элитный фрилансер. Твоя задача - написать короткий и бьющий в цель отклик (до 400 символов).\n\n"
        "ЖЕСТКИЕ ПРАВИЛА:\n"
        "1. Без воды ('Здравствуйте', 'Готов взяться'). Начинай сразу с дела (например: 'Приветствую! По вашей задаче:').\n"
        "2. СТРОГО опирайся на предоставленные данные анализа. Если в 'Формате результата' указан диск/папки/архив — НИКОГДА не предлагай таблицы CSV/Excel/JSON!\n"
        "3. Общайся на уровне клиента (если он бизнесмен - меньше сложных терминов, больше пользы).\n"
        "4. В конце задай ОДИН уточняющий вопрос строго по сути задачи."
    )
    
    generator_user = (
        f"📋 ДАННЫЕ АНАЛИЗА ЗАКАЗА:\n"
        f"- Главная задача: {analysis_data.get('core_task')}\n"
        f"- Нужный стек: {analysis_data.get('optimal_stack')}\n"
        f"- Формат результата: {analysis_data.get('result_format')}\n"
        f"- Уровень клиента: {analysis_data.get('client_level')}\n\n"
        f"Напиши текст отклика для клиента."
    )
    
    print("✍️ [Генератор] Пишу отклик на основе анализа...")
    final_reply = await send_to_openrouter(generator_system, generator_user)
    
    # Очистка от возможных кавычек, если ИИ решит их добавить
    final_reply = final_reply.strip('`"\' ')
    
    print("✅ [Генератор] Отклик готов!")
    return final_reply