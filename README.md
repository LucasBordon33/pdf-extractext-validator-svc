# pdf-validator-service

Microservicio **stateless** en **Python (FastAPI)** diseñado exclusivamente para recibir archivos en memoria y validar su integridad estructural como formato PDF.

Al procesar todo mediante `io.BytesIO`, el contenedor nunca escribe en disco, lo que facilita el escalado horizontal y el despliegue de múltiples réplicas sin estado.

---

## Arquitectura y Principios

El proyecto aplica una **arquitectura por capas desacopladas**:

* **`api/`**: Handlers HTTP (`UploadFile`), conversión a DTOs y manejo de códigos HTTP.
* **`core/`**: Lógica de negocio pura independiente del framework web.
* **`schemas/`**: DTOs de Pydantic para el contrato de la API.

### Decisiones Clave
* **Pipeline en Memoria:** Análisis ordenado de costo creciente: comprobación de tamaño $\rightarrow$ tipo MIME real (sniffing de bytes con `python-magic`) $\rightarrow$ marcadores crudos (`%PDF`, `%%EOF`) $\rightarrow$ estructura profunda con `pypdf`.
* **Contrato Estable:** Los PDFs inválidos o corruptos retornan un HTTP `200` con `is_valid: false` y su lista de errores. Exceder el tamaño límite retorna HTTP `413`.
* **Inspección Segura:** La validación MIME analiza los bytes del archivo y no confía en la cabecera `Content-Type` enviada por el cliente.

---

## Stack Tecnológico

* **Lenguaje & Web:** Python 3.11, FastAPI, Uvicorn, Pydantic v2 (`pydantic-settings`).
* **Validación:** `python-magic` (MIME sniffing), `pypdf` (análisis estructural).
* **Testing & Tooling:** `pytest`, `httpx`, `ruff`.

---

## Estructura del Proyecto

```text
pdf-validator-service/
├── app/
│   ├── main.py              # Punto de entrada de la app
│   ├── config.py            # Gestión de variables de entorno
│   ├── api/v1/endpoints/    # Rutas HTTP (/health, /validate)
│   ├── core/                # Lógica pura de validación y excepciones
│   └── schemas/             # Modelos Pydantic (Request/Response)
├── tests/                   # Pruebas unitarias e integración
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml            # Configuración del proyecto y dependencias

API Reference
GET /health
Estado del servicio para orquestadores/healthchecks.

{
  "status": "ok",
  "version": "0.1.0"
}

POST /api/v1/validate
Acepta un archivo vía multipart/form-data (campo file).

PDF Válido (200 OK):

JSON
{
  "is_valid": true,
  "filename": "documento.pdf",
  "errors": []
}

PDF Corrupto o Inválido (200 OK):

JSON
{
  "is_valid": false,
  "filename": "archivo.pdf",
  "errors": [
    {
      "code": "INCOMPLETE_PDF",
      "message": "missing '%%EOF' marker at end of stream",
      "detail": "El archivo está incompleto o truncado."
    }
  ]
}


