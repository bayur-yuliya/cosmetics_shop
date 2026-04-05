FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN groupadd -r appgroup && useradd -r -g appgroup -m -d /home/appuser appuser

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    gettext \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

RUN poetry install --only main --no-interaction --no-ansi --no-root

RUN mkdir -p /app/staticfiles /app/media/default /app/media/product_images && \
    chown -R appuser:appgroup /app/staticfiles /app/media && \
    chmod -R 755 /app/media

COPY --chown=appuser:appgroup . .

RUN chmod +x /app/entrypoint.sh /app/src/manage.py

USER appuser
WORKDIR /app/src
ENV PYTHONPATH=/app/src

RUN python manage.py compilemessages

ENTRYPOINT ["/app/entrypoint.sh"]

#CMD ["gunicorn", "config.wsgi:application", \
#     "--bind", "0.0.0.0:8000", \
#     "--workers", "3", \
#     "--timeout", "120"]