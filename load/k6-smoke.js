// Smoke de carga para CI - Validador PDF (MS3)
// Uso local:  k6 run -e BASE_URL=http://localhost:8001 load/k6-smoke.js
import http from "k6/http";
import { check } from "k6";
import encoding from "k6/encoding";

export const options = {
  vus: 10,
  duration: "10s",
  thresholds: {
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<15000"],
  },
};

// Usar un PDF del dataset de stress (ya montado en docker compose para el perfil stress/CI)
const pdfBytes = open("../tests/stress/pdfs/1.pdf", "b");
const pdfB64 = encoding.b64encode(pdfBytes);

const BASE_URL = __ENV.BASE_URL || "http://localhost:8001";

export default function () {
  const payload = JSON.stringify({
    name: "smoke.pdf",
    content_base64: pdfB64,
  });

  const response = http.post(`${BASE_URL}/validate`, payload, {
    headers: { "Content-Type": "application/json" },
    timeout: "30s",
  });

  check(response, {
    "status 200": (r) => r.status === 200,
    "contrato valid/errores": (r) => {
      if (r.status !== 200) return false;
      try {
        const body = r.json();
        return typeof body.valid === "boolean" && Array.isArray(body.errors);
      } catch (e) {
        return false;
      }
    },
  });
}
