#!/bin/bash

HOST=${1:-http://host.docker.internal}
DURACAO=${TEST_DURATION:-60s}
TAXA=${SPAWN_RATE:-5}

mkdir -p /app/results

echo "============================================"
echo " i-Educar — Testes de Performance"
echo " Alvo: $HOST"
echo "============================================"

for USUARIOS in 10 50 100; do
  echo ""
  echo ">>> Login — $USUARIOS usuários..."
  locust --headless --host="$HOST" --users="$USUARIOS" --spawn-rate=5 \
    --run-time="$DURACAO" \
    --csv="/app/results/login_${USUARIOS}u" \
    --html="/app/results/login_${USUARIOS}u.html" \
    -f /app/locustfile.py --class-picker UsuarioLoginTeste || true
  sleep 5

  echo ""
  echo ">>> Aluno — $USUARIOS usuários..."
  locust --headless --host="$HOST" --users="$USUARIOS" --spawn-rate=5 \
    --run-time="$DURACAO" \
    --csv="/app/results/aluno_${USUARIOS}u" \
    --html="/app/results/aluno_${USUARIOS}u.html" \
    -f /app/locustfile.py --class-picker UsuarioAlunoTeste || true
  sleep 5
done

echo ""
echo "Todos os testes concluídos. Resultados em /app/results/"