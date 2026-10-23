/**
 * Spike test k6 - MS3 Validador
 * Escenario: 0 -> 100 VUs en 10 s, sostener 100 VUs por 20 s, bajar a 0 en 10 s
 */
import http from 'k6/http';
import { check } from 'k6';
import { b64encode } from 'k6/encoding';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8001';
const VALIDATE_PATH = __ENV.VALIDATE_PATH || '/validate';

export const options = {
  stages: [
    { duration: '10s', target: 100 }, // ramp-up
    { duration: '20s', target: 100 }, // meseta
    { duration: '10s', target: 0 },   // ramp-down
  ],
  discardResponseBodies: false,
  summaryTrendStats: ['min', 'avg', 'p(50)', 'p(90)', 'p(95)', 'max', 'count'],
  thresholds: {
    http_req_failed: ['rate==0'],
    checks: ['rate>0.99'],
    http_req_duration: [
      `p(50)<${__ENV.MAX_P50 || 2000}`,
      `p(90)<${__ENV.MAX_P90 || 8000}`,
      `p(95)<${__ENV.MAX_P95 || 9000}`,
      `max<${__ENV.MAX_MAX || 15000}`,
    ],
  },
};

http.setResponseCallback(http.expectedStatuses(200));

const PDF_FILES = (__ENV.PDF_FILES || 'prueba.pdf')
  .split(',')
  .map((name) => name.trim())
  .filter((name) => name.length > 0);

const documents = PDF_FILES.map((name) => {
  const bytes = open(`pdfs/${name}`, 'b');
  return { name, bytes, b64: b64encode(bytes) };
});

export default function () {
  const doc = documents[Math.floor(Math.random() * documents.length)];
  const payload = JSON.stringify({
    name: doc.name,
    content_base64: doc.b64,
  });

  const res = http.post(
    `${BASE_URL}${VALIDATE_PATH}`,
    payload,
    { headers: { 'Content-Type': 'application/json' }, tags: { name: 'spike-validate' } }
  );

  check(res, {
    'status es 200': (r) => r.status === 200,
    'valid es boolean': (r) => {
      try {
        const v = r.json('valid');
        return typeof v === 'boolean';
      } catch (e) {
        return false;
      }
    },
  });
}
