# ── Estágio único: Python 3.11 slim ────────────────────────────────────────
FROM python:3.11-slim

LABEL maintainer="seu-email@exemplo.com"
LABEL description="i-educar — testes de performance com Locust"

# Variáveis de ambiente com defaults
ENV TARGET_HOST=http://host.docker.internal:8000 \
    IEDUCAR_USER=comunidade \
    IEDUCAR_PASS=Comunidade@1 \
    TEST_DURATION=60s \
    SPAWN_RATE=5 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependências do sistema (para matplotlib renderizar em modo headless)
RUN apt-get update && apt-get install -y --no-install-recommends \
        bash \
        curl \
        libfreetype6-dev \
        libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY . .

# Garante que os diretórios de saída existem e têm permissão
RUN mkdir -p results/10users results/50users results/100users reports \
    && chmod +x run_tests.sh

# Volume para persistir resultados fora do container
VOLUME ["/app/results", "/app/reports"]

# Entrypoint padrão: executa todos os testes e gera relatório
CMD ["bash", "-c", "./run_tests.sh ${TARGET_HOST} && python scripts/generate_report.py"]