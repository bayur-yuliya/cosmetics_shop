FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN groupadd -r appgroup && useradd -r -g appgroup -m -d /home/appuser appuser

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./
# Авто-фикс лок-файла, о котором ругался Docker
RUN poetry lock --regenerate && \
    poetry install --only main --no-interaction --no-ansi --no-root

# Создаем структуру и даем права.
# ВАЖНО: создаем и подпапку для картинок, чтобы Django не споткнулся
RUN mkdir -p /app/static /app/media/default /app/media/product_images && \
    chown -R appuser:appgroup /app/static /app/media && \
    chmod -R 755 /app/media

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh && chown appuser:appgroup /app/entrypoint.sh

COPY --chown=appuser:appgroup . .

USER appuser
WORKDIR /app/src
ENV PYTHONPATH=/app/src

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--timeout", "120"]