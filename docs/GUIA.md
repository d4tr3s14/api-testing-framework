# 📘 Guía detallada (para todos los niveles)

Esta guía explica **paso a paso** cómo ejecutar, entender y editar el proyecto
**api-testing-framework**, desde tu computador hasta lo que ocurre en GitHub
cuando se ejecuta el CI. Pensada para que **alguien junior** pueda hacerlo sin
complicaciones.

> Orden sugerido: **1)** ¿Qué es? → **2)** Glosario → **3)** Frameworks →
> **4)** Requisitos → **5)** Clonar → **6)** Ejecución local → **7)** Reportes →
> **8)** Cómo editar → **9)** Qué hace el CI.

---

## 1. ¿Qué es este proyecto?

Es un framework para **probar APIs REST** (servicios que devuelven datos por
HTTP, normalmente en JSON). Verifica que la API responda lo correcto: los
**códigos de estado** correctos (200, 401, 404, 422…), el **cuerpo** esperado,
reglas de **seguridad** (autenticación), **límites** (paginación) y que el
**contrato** (la forma del JSON) no cambie sin avisar.

Trae **su propia API de prueba** (un servicio **FastAPI** que se levanta solo en
un puerto local), así que **corre sin depender de servicios externos**. Usa
**pytest** y genera reportes **Allure** con la petición y respuesta de cada test.

```
pytest ─► tests/*.py ─► utils/api_client (HTTP) ─► FastAPI app (app/) ─► Allure
```

---

## 2. Glosario (términos clave)

| Término | Qué significa, en simple |
|---------|--------------------------|
| **API REST** | Un servicio al que le pides datos por HTTP (ej. `GET /api/customers`). |
| **Endpoint** | Una ruta de la API (ej. `POST /api/auth/token`). |
| **Código de estado** | El número que indica el resultado: `200` OK, `401` no autorizado, `404` no existe, `422` datos inválidos. |
| **Payload / Body** | El contenido (JSON) que se envía o se recibe. |
| **Token / Bearer** | Una "credencial" que se manda en la cabecera para autenticarse. |
| **Contract testing** | Verificar que la respuesta cumple una **forma** definida (JSON Schema). |
| **JSON Schema** | Un documento que describe cómo debe ser un JSON (campos, tipos, obligatorios). |
| **Happy path** | El camino correcto/exitoso. |
| **Negative path** | Casos de error a propósito (token malo, datos inválidos…). |
| **Boundary** | Casos límite (ej. pedir página 0 o un tamaño fuera de rango). |
| **pytest** | El framework de pruebas de Python. |
| **Fixture** | Pieza reutilizable que prepara algo (aquí, levantar la API antes de las pruebas). |
| **Parametrize** | Repetir un test con varios datos distintos (data-driven). |
| **SUT** | *System Under Test*, el sistema bajo prueba (aquí, la API FastAPI de `app/`). |
| **Allure** | Reporte interactivo con el detalle de cada prueba (request/response). |
| **CI** | Automatización que corre las pruebas en GitHub en cada cambio. |
| **gh-pages** | Rama donde se publica el reporte Allure como sitio web. |

---

## 3. Frameworks y lenguajes (para qué sirve cada uno)

| Herramienta | Lenguaje | ¿Para qué sirve **en este proyecto**? |
|-------------|----------|----------------------------------------|
| **Python** | — | Lenguaje base del framework. |
| **pytest** | Python | El **ejecutor** de pruebas. |
| **requests** | Python | Cliente HTTP: hace las llamadas a la API. |
| **jsonschema** | Python | Valida que las respuestas cumplan el **contrato** (JSON Schema). |
| **allure-pytest** | Python | Genera el reporte **Allure** y adjunta request/response. |
| **FastAPI** | Python | El **SUT**: la API de prueba con sus endpoints. |
| **Uvicorn** | Python | El **servidor** que levanta la API FastAPI en un puerto local. |
| **GitHub Actions** | YAML | El **CI**: corre las pruebas y publica el reporte. |

---

## 4. Requisitos previos

1. **Python 3.10+** → https://www.python.org/downloads/ (`python --version`).
2. **Git** → https://git-scm.com/
3. *(Opcional, para el dashboard)* **Allure CLI** → `npm install -g allure-commandline`.

> No necesitas configurar nada externo: la API de prueba se levanta **sola**.

---

## 5. Clonar el proyecto

```bash
git clone https://github.com/d4tr3s14/api-testing-framework.git
cd api-testing-framework
```

---

## 6. Ejecución LOCAL paso a paso

### Paso 1 — Entorno virtual e instalación
```bash
python -m venv .venv
```
Actívalo:
- **Windows (PowerShell):** `.\.venv\Scripts\Activate.ps1`
- **Linux / macOS:** `source .venv/bin/activate`

Instala dependencias:
```bash
pip install -r requirements.txt
```

### Paso 2 — Ejecutar las pruebas
```bash
pytest
```
La API de prueba se **levanta automáticamente** (no tienes que iniciarla tú).
Verás algo como `39 passed in ~2s`.

### Paso 3 — Con dashboard Allure (un comando)
- **Windows (PowerShell):** `.\scripts\run_demo.ps1`
- **Linux / macOS:** `./scripts/run_demo.sh`

O manualmente:
```bash
pytest --alluredir=allure-results
allure serve allure-results
```

### Explorar la API a mano (opcional)
```bash
uvicorn app.main:app --reload
# luego abre http://127.0.0.1:8000/docs  (documentación interactiva Swagger)
```

---

## 7. Reportes

- **Allure** muestra cada prueba con su **petición y respuesta** adjuntas, así
  cualquier resultado es trazable. Ábrelo con `allure serve allure-results`.

---

## 8. Cómo EDITAR el proyecto (recetas para junior)

### a) Agregar una prueba nueva
Crea o edita un archivo en `tests/` (deben empezar con `test_`). Ejemplo:
```python
def test_health_ok(api_client):
    resp = api_client.get("/health")
    assert resp.status_code == 200
```
`pytest` lo descubre automáticamente.

### b) Pruebas data-driven (varios casos)
```python
import pytest

@pytest.mark.parametrize("page_size", [0, 999])
def test_pagination_out_of_range(api_client, page_size):
    resp = api_client.get(f"/api/customers?page_size={page_size}")
    assert resp.status_code == 422
```

### c) Agregar/editar un contrato (JSON Schema)
Los esquemas viven en `tests/schemas/`. Crea uno nuevo (ej. `order.json`) y
valídalo en una prueba con `utils/schema_validator.py`.

### d) Agregar un endpoint a la API de prueba
Edita `app/main.py` (las rutas) y `app/data.py` (los datos en memoria).

### e) Entender dónde está cada cosa
- `tests/*.py` → las pruebas (el **qué**).
- `utils/api_client.py` → el cliente HTTP que usan las pruebas.
- `utils/schema_validator.py` → valida respuestas contra JSON Schema.
- `conftest.py` → **levanta la API** antes de las pruebas y la apaga al final.
- `app/` → la API FastAPI bajo prueba.

---

## 9. ¿Qué hace el CI en GitHub? (paso a paso)

El CI vive en `.github/workflows/ci.yml` y corre en cada `push`/`pull request`:

1. **Set up Python + install** — instala Python y `requirements.txt`.
2. **Run API test suite** — `pytest --alluredir=allure-results` (la API se
   levanta sola dentro de las pruebas).
3. **Upload Allure results** — guarda los resultados como artefacto descargable.
4. **Job `publish-report` (solo en push)** — genera el reporte **Allure** y lo
   **publica en GitHub Pages** (rama `gh-pages`).

### ¿Dónde veo el resultado?
- GitHub → pestaña **Actions** → el run (✅ / ❌).
- Reporte Allure en vivo: **https://d4tr3s14.github.io/api-testing-framework/**
  (requiere GitHub Pages activado en *Settings → Pages → rama `gh-pages`*).

---

## 10. Problemas comunes

| Problema | Solución |
|----------|----------|
| `pytest: command not found` | Activa el `.venv` y `pip install -r requirements.txt`. |
| Las pruebas no encuentran la API | La levanta `conftest.py` sola; si falla, revisa que el puerto esté libre. |
| `allure: command not found` | Instala el CLI: `npm install -g allure-commandline`. |
| PowerShell bloquea el script | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`. |
| El badge de Allure da 404 | Falta activar GitHub Pages (rama `gh-pages`). |

---

## 11. Mapa de archivos

```
tests/                 las pruebas (test_auth, test_customers, test_balances, ...)
  schemas/             contratos JSON Schema para las respuestas
utils/
  api_client.py        cliente HTTP que usan las pruebas
  schema_validator.py  valida respuestas contra JSON Schema
app/                   la API FastAPI bajo prueba (main.py = rutas, data.py = datos)
conftest.py            levanta/apaga la API automáticamente para las pruebas
pytest.ini             configuración de pytest
scripts/run_demo.*     corre la suite y abre Allure
.github/workflows/ci.yml  el pipeline de CI
```

---

¿Dudas? Empieza por la **sección 6** (instalar y `pytest`): la API se levanta
sola, así que verás resultados en segundos.
