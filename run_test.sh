#!/bin/bash
set -e

HOST=${1:-http://host.docker.internal:8080}
DURACAO=${TEST_DURATION:-60s}
TAXA=${SPAWN_RATE:-5}

mkdir -p /app/results

echo "============================================"
echo " i-Educar — Testes de Performance"
echo " Alvo: $HOST"
echo "============================================"

for USUARIOS in 10 50 100; do
  echo ""
  echo ">>> Rodando com $USUARIOS usuários simultâneos..."

  locust \
    --headless \
    --host="$HOST" \
    --users="$USUARIOS" \
    --spawn-rate="$TAXA" \
    --run-time="$DURACAO" \
    --csv="/app/results/resultado_${USUARIOS}u" \
    --html="/app/results/relatorio_${USUARIOS}u.html" \
    -f /app/locustfile.py

  echo ">>> Concluído: $USUARIOS usuários"
  sleep 5
done

echo ""
echo "Todos os testes concluídos. Resultados em /app/results/"