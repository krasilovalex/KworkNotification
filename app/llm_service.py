import aiohttp
from .config import OPENROUTER_API_KEY, LLM_MODEL

async def generate_cover_letter(title: str, description: str) -> str:

    if not OPENROUTER_API_KEY:
        return "API KEY OPENROUTER NOT FOUND"
    
    system_prompt = (
        "Ты — опытный Backend-разработчик (Python, FastAPI, Docker). "
        "Твоя задача — писать короткие, профессиональные и продающие отклики на фриланс-заказы. "
        "Пиши без воды, не используй шаблонные фразы типа 'Я готов взяться за работу'. "
        "Сразу пиши, как ты решишь задачу. Длина: до 500 символов. Отвечай на русском языке."
    )

    user_prompt = f"Напиши отклик для этого заказа.\n\nНазвание: {title}\nОписание: {description}"

    headers = {
        "Authorization" : f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type" : "application/json",
        "HTTP-Referer": "https://github.com/KworkNotification",
        "X-Title": "KworkNoti Bot"
    }

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post("https://openrouter.ai/api/v1/chat/completions",headers=headers, json=payload, timeout=15) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    return f"ERROR API ({resp.status}):{error_text}"
                
                data = await resp.json()


                return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Ошибка сети при запросе к LLM: {e}"