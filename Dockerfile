# ── Estágio único: Python 3.11 slim ────────────────────────────────────────
FROM python:3.11-slim

LABEL maintainer="seu-email@exemplo.com"
LABEL description="i-educar — testes de performance com Locust"

ENV TARGET_HOST=http://host.docker.internal:8000 \
    IEDUCAR_USER=comunidade \
    IEDUCAR_PASS=Comunidade@1 \
    TEST_DURATION=60s \
    SPAWN_RATE=5 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        bash \
        curl \
        libfreetype6-dev \
        libpng-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p results reports \
    && chmod +x run_test.sh

VOLUME ["/app/results", "/app/reports"]

CMD ["bash", "-c", "./run_test.sh ${TARGET_HOST}"]