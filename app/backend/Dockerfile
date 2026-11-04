FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Kod değişince bağımlılıklar yeniden kurulmasın diye önce requirements kopyalanır
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY alembic.ini .
COPY migrations ./migrations
COPY app ./app

RUN useradd --uid 1000 --no-create-home --shell /usr/sbin/nologin appuser
USER 1000

EXPOSE 8000

# exec formu: SIGTERM doğrudan uvicorn'a ulaşır, graceful shutdown çalışır
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
