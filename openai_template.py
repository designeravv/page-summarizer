"""Базовый модуль для работы с OpenAI-совместимым API (polza.ai)."""

import os
import time
import logging
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

logger = logging.getLogger(__name__)

POLZA_API_KEY: str = os.getenv("POLZA_API_KEY", "")
if not POLZA_API_KEY:
    raise ValueError("POLZA_API_KEY not found in environment variables")

BASE_URL: str = "https://api.polza.ai/api/v1"
MODEL: str = "openai/gpt-4o"
MAX_RETRIES: int = 3
RETRY_DELAY: float = 2.0

client = OpenAI(
    api_key=POLZA_API_KEY,
    base_url=BASE_URL,
)


def ask_openai(system_prompt: str, user_message: str) -> str:
    """
    Отправляет запрос к LLM через polza.ai.

    Args:
        system_prompt: Системный промпт (роль агента).
        user_message: Пользовательское сообщение / контент.

    Returns:
        Ответ модели в виде строки.

    Raises:
        RuntimeError: если все попытки исчерпаны.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    last_error: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info("Запрос к %s (попытка %d/%d)…", MODEL, attempt, MAX_RETRIES)
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.3,
                max_tokens=1024,
            )
            result: str = response.choices[0].message.content.strip()
            logger.info("Ответ получен (%d символов).", len(result))
            return result

        except Exception as exc:
            last_error = exc
            logger.warning("Ошибка (попытка %d): %s", attempt, exc)
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)

    raise RuntimeError(
        f"Не удалось получить ответ после {MAX_RETRIES} попыток. "
        f"Последняя ошибка: {last_error}"
    )
