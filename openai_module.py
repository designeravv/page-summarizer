"""Модуль агента: загрузка страницы и генерация резюме."""

import logging
import requests
from bs4 import BeautifulSoup

from openai_template import ask_openai

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT: int = 15
USER_AGENT: str = "Mozilla/5.0 (compatible; PageSummarizerBot/1.0)"

SYSTEM_PROMPT: str = (
    "Ты — аналитик. Тебе дан текст веб-страницы. "
    "Сформулируй суть этого текста в 3–5 предложениях на языке оригинала. "
    "Не добавляй вводных фраз вроде «Вот резюме» или «Данный текст…». "
    "Просто дай сжатое, информативное резюме."
)


def fetch_page_text(url: str) -> str:
    """
    Загружает HTML по URL и возвращает чистый текст.

    Args:
        url: Адрес веб-страницы.

    Returns:
        Извлечённый текст страницы.

    Raises:
        requests.RequestException: при сетевых ошибках.
        ValueError: если страница не содержит текста.
    """
    logger.info("Загружаю страницу: %s", url)
    response = requests.get(
        url,
        timeout=REQUEST_TIMEOUT,
        headers={"User-Agent": USER_AGENT},
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Убираем лишние теги
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "aside"]):
        tag.decompose()

    text: str = soup.get_text(separator="\n", strip=True)

    if not text:
        raise ValueError("Страница не содержит извлекаемого текста.")

    logger.info("Извлечено %d символов.", len(text))
    return text


def summarize_url(url: str) -> str:
    """
    Главная функция агента: загружает страницу и возвращает резюме.

    Args:
        url: Адрес веб-страницы.

    Returns:
        Краткое резюме в 3–5 предложениях.
    """
    # 1. Загружаем текст
    page_text: str = fetch_page_text(url)

    # 2. Обрезаем, если слишком длинный (лимит контекста)
    max_chars: int = 10_000
    if len(page_text) > max_chars:
        logger.warning("Текст обрезан: %d → %d символов.", len(page_text), max_chars)
        page_text = page_text[:max_chars] + "\n\n[Текст обрезан…]"

    # 3. Получаем резюме от LLM
    summary: str = ask_openai(
        system_prompt=SYSTEM_PROMPT,
        user_message=page_text,
    )

    return summary
