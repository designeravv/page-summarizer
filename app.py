"""Flask-приложение: веб-интерфейс агента «Краткое резюме страницы»."""

from flask import Flask, render_template, request
import logging

from openai_module import summarize_url

# ─── Логирование ───
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    """Главная страница: форма ввода URL и отображение результата."""
    summary: str | None = None
    url: str = ""
    error: str | None = None

    if request.method == "POST":
        url = request.form.get("url", "").strip()

        if not url:
            error = "Пожалуйста, введите URL."
        else:
            # Добавляем схему, если забыли
            if not url.startswith(("http://", "https://")):
                url = "https://" + url

            try:
                summary = summarize_url(url)
                logger.info("Резюме для %s успешно сформировано.", url)
            except Exception as exc:
                error = f"Ошибка: {exc}"
                logger.error("Ошибка при обработке %s: %s", url, exc)

    return render_template(
        "index.html",
        summary=summary,
        url=url,
        error=error,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
