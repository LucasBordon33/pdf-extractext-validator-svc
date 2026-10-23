#!/bin/sh
# Carga fija con Vegeta - MS3 Validador (POST /validate JSON)
# Compatible con host (bash/python3) y con la imagen Alpine peterevans/vegeta.
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
RESULTS_DIR="$SCRIPT_DIR/results"
PDFS_DIR="$SCRIPT_DIR/pdfs"

BASE_URL="${BASE_URL:-http://localhost:8001}"
RATE="${RATE:-25/2s}"
DURATION="${DURATION:-30s}"
TIMEOUT="${TIMEOUT:-30s}"

mkdir -p "$RESULTS_DIR"
rm -f "$RESULTS_DIR"/res*.bin "$RESULTS_DIR"/body_*.json "$RESULTS_DIR"/reporte*.bin "$RESULTS_DIR"/reporte*.txt "$RESULTS_DIR"/reporte*.json

echo "== Vegeta: Open Model ${DURATION} a 50 req/s contra $BASE_URL/validate =="

# 4 ataques paralelos: un PDF por proceso (rotación del dataset)
for i in 1 2 3 4; do
  BODY_FILE="$RESULTS_DIR/body_$i.json"

  # Generar el JSON con content_base64 (python3 si existe; si no, base64 POSIX)
  if command -v python3 >/dev/null 2>&1; then
    python3 -c "import base64, json, sys; data = open('$PDFS_DIR/$i.pdf','rb').read(); payload = {'name': f'$i.pdf', 'content_base64': base64.b64encode(data).decode('ascii')}; sys.stdout.write(json.dumps(payload))" > "$BODY_FILE"
  else
    B64=$(base64 "$PDFS_DIR/$i.pdf" | tr -d '\n')
    printf '{"name":"%s.pdf","content_base64":"%s"}' "$i" "$B64" > "$BODY_FILE"
  fi

  # Pasar target por stdin y body por -body
  echo "POST $BASE_URL/validate" | vegeta attack \
    -rate="$RATE" \
    -duration="$DURATION" \
    -timeout="$TIMEOUT" \
    -header "Content-Type: application/json" \
    -body="$BODY_FILE" \
    > "$RESULTS_DIR/res$i.bin" &
done

# Esperar a que los 4 ataques concurrentes finalicen
wait

echo "== Generando reportes =="
vegeta report "$RESULTS_DIR"/res*.bin | tee "$RESULTS_DIR/reporte.txt"
vegeta report -type=json "$RESULTS_DIR"/res*.bin > "$RESULTS_DIR/reporte.json"
