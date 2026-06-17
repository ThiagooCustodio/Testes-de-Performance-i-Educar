#!/bin/bash

HOST=${1:-http://host.docker.internal}
DURACAO=${TEST_DURATION:-60s}

mkdir -p /app/results

echo "============================================"
echo " i-Educar - Testes de Performance"
echo " Alvo: $HOST"
echo "============================================"

# --- Login ---
for USUARIOS in 1 5 10; do
  echo ""
  echo ">>> Login - $USUARIOS usuarios..."
  locust --headless --host="$HOST" --users="$USUARIOS" --spawn-rate=5 \
    --run-time="$DURACAO" \
    --csv="/app/results/login_${USUARIOS}u" \
    --html="/app/results/login_${USUARIOS}u.html" \
    -f /app/locustfile.py --class-picker UsuarioLoginTeste || true
  sleep 5
done

# --- Aluno ---
for USUARIOS in 1 5 10; do
  echo ""
  echo ">>> Aluno - $USUARIOS usuarios..."
  locust --headless --host="$HOST" --users="$USUARIOS" --spawn-rate=5 \
    --run-time="$DURACAO" \
    --csv="/app/results/aluno_${USUARIOS}u" \
    --html="/app/results/aluno_${USUARIOS}u.html" \
    -f /app/locustfile.py --class-picker UsuarioAlunoTeste || true
  sleep 5
done

# --- Consulta ---
for USUARIOS in 1 5 10; do
  echo ""
  echo ">>> Consulta - $USUARIOS usuarios..."
  locust --headless --host="$HOST" --users="$USUARIOS" --spawn-rate=5 \
    --run-time="$DURACAO" \
    --csv="/app/results/consulta_${USUARIOS}u" \
    --html="/app/results/consulta_${USUARIOS}u.html" \
    -f /app/locustfile.py --class-picker UsuarioConsultaTeste || true
  sleep 5
done

# --- Exportacao ---
for USUARIOS in 1 5 10; do
  echo ""
  echo ">>> Exportacao de Usuarios - $USUARIOS usuarios..."
  locust --headless --host="$HOST" --users="$USUARIOS" --spawn-rate=5 \
    --run-time="$DURACAO" \
    --csv="/app/results/exportacao_${USUARIOS}u" \
    --html="/app/results/exportacao_${USUARIOS}u.html" \
    -f /app/locustfile.py --class-picker UsuarioExportacaoTeste || true
  sleep 5
done

# --- Navegacao ---
for USUARIOS in 1 5 10; do
  echo ""
  echo ">>> Navegacao - $USUARIOS usuarios..."
  locust --headless --host="$HOST" --users="$USUARIOS" --spawn-rate=5 \
    --run-time="$DURACAO" \
    --csv="/app/results/navegacao_${USUARIOS}u" \
    --html="/app/results/navegacao_${USUARIOS}u.html" \
    -f /app/locustfile.py --class-picker UsuarioNavegacaoTeste || true
  sleep 5
done

echo ""
echo "Todos os testes concluidos. Resultados em /app/results/"