FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/Backend \
    RUN_SEED_DATA=false \
    SEED_DATA_RESEED=false

WORKDIR /app/Backend

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . /app/Backend

RUN chmod +x /app/Backend/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/Backend/docker-entrypoint.sh"]
