#!/usr/bin/env bash
# Orquestador de pruebas de carga - MS3 Validador
# Usa los servicios del perfil `stress` de docker compose (no requiere k6/vegeta en el host).
set -euo pipefail

RESULTS_DIR="tests/stress/results"
PDF_FILES="${PDF_FILES:-prueba.pdf}"
READY_ATTEMPTS="${READY_ATTEMPTS:-60}"
COMPOSE="docker compose"

mkdir -p "$RESULTS_DIR"

echo "== Reset del stack: down -v =="
$COMPOSE down -v
echo "== Rebuild y levantado: up --build -d =="
$COMPOSE up --build -d

echo "== Esperando validador healthy (max ${READY_ATTEMPTS}s) =="
ready=0
for _ in $(seq 1 "$READY_ATTEMPTS"); do
  container=$($COMPOSE ps -q validator || true)
  if [ -n "$container" ]; then
    status=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}running{{end}}' "$container" 2>/dev/null || echo unknown)
    if [ "$status" = "healthy" ]; then
      ready=1
      echo "   validator healthy"
      break
    fi
  fi
  sleep 1
done
if [ "$ready" -ne 1 ]; then
  echo "ERROR: el validador no quedo healthy a tiempo" >&2
  $COMPOSE ps
  exit 1
fi

echo "== k6: spike 100 VUs =="
k6_code=0
$COMPOSE --profile stress run --rm k6 \
  run -e PDF_FILES="$PDF_FILES" \
  --summary-export=/tests/stress/results/k6_summary.json \
  /tests/stress/spike.js || k6_code=$?
echo "   k6 exit code: $k6_code"

echo "== Vegeta: carga fija 50 req/s =="
$COMPOSE --profile stress run --rm vegeta

echo "== Comparador de resultados =="
if command -v uv >/dev/null 2>&1; then
  uv run python tests/stress/compare.py
  exit_code=$?
else
  python tests/stress/compare.py
  exit_code=$?
fi
echo "== Orquestador finalizado (exit $exit_code) =="
exit $exit_code
