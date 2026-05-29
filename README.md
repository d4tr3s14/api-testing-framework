# API Testing Framework

[![CI](https://github.com/d4tr3s14/api-testing-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/d4tr3s14/api-testing-framework/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![pytest](https://img.shields.io/badge/tested%20with-pytest-0a9edc.svg)
![Contract testing](https://img.shields.io/badge/contracts-JSON%20Schema-6f42c1.svg)
![Reporting](https://img.shields.io/badge/reporting-Allure-orange.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A **professional REST API testing framework** built with `pytest` + `requests`,
covering functional, security, boundary, and **contract (JSON Schema)** testing,
with **Allure** reporting and CI.

> **Runs out of the box.** The framework ships with the system under test — a
> small but realistic FastAPI service — which is started automatically on a free
> local port. Clone, install, `pytest`. No external APIs, no credentials, no
> flakiness.

```
39 passed in ~2s
```

## Why this project

API quality issues are subtle: a `200` with the wrong body, a missing `401`, a
contract that silently drifts. This framework exercises an API the way a senior
QA engineer would:

- **Positive** paths (happy path, correct status codes and payloads)
- **Negative** paths (`401` auth failures, `404` not found, `422` validation)
- **Boundary** conditions (pagination limits, field constraints)
- **Contract** testing (responses validated against JSON Schema)
- **Business rules** (e.g. balance share distribution must sum to 100%)

It is the **API-layer companion** to
[`data-quality-framework`](https://github.com/d4tr3s14/data-quality-framework):
both test the same fictional multi-fund investment platform, **"Veridian"** —
one at the data/warehouse layer, this one at the API layer. All data is
fictional and synthetic.

## What's tested

| Suite | Category | Highlights |
|---|---|---|
| `test_health.py` | Smoke | service liveness, no auth |
| `test_auth.py` | Security / negative | Bearer token issuance, `401` on bad/missing/invalid token, `422` on malformed body |
| `test_customers.py` | Functional / boundary | listing, pagination (incl. out-of-range → `422`), segment filter, `404`, `201` create, `422` validation |
| `test_balances.py` | Functional / business rule | balances retrieval, **share % sums to 100** |
| `test_contracts.py` | Contract | every response validated against a JSON Schema |

**39 tests**, data-driven via `pytest.mark.parametrize`, fully isolated
(in-memory state reset before each test).

## Architecture

```
pytest ──▶ tests/*.py ──▶ utils/api_client.py ──(HTTP, requests)──▶ FastAPI app
                      └──▶ utils/schema_validator.py (JSON Schema)        (app/)
conftest.py starts the app with uvicorn on a free port and tears it down after.
```

The tests talk to the API over **real HTTP on localhost** (not in-process), so
they behave exactly as they would against a deployed service. See
[docs/architecture.md](docs/architecture.md) for details.

## Quickstart

### Prerequisites

- Python 3.10+
- (Optional, for the dashboard) [Allure CLI](https://allurereport.org/docs/install/) —
  e.g. `npm install -g allure-commandline`

### 1. Set up the environment

```bash
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Run the tests

```bash
pytest
```

### 3. Run with the Allure dashboard (one command)

**Windows (PowerShell):**

```powershell
.\scripts\run_demo.ps1
```

> If you get an execution-policy error, allow scripts for the current session
> first: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`

**Linux / macOS:**

```bash
./scripts/run_demo.sh
```

Each test attaches its **request and response** to the Allure report, so every
result is fully traceable.

## Explore the API manually (optional)

The system under test is a real FastAPI app with interactive Swagger docs:

```bash
uvicorn app.main:app --reload
# then open http://127.0.0.1:8000/docs
```

Demo credentials for `POST /auth/token`: `client_id=veridian-demo`,
`client_secret=demo-secret`.

## Project structure

```
api-testing-framework/
├── app/                      # System under test (local FastAPI mock API)
│   ├── main.py               # Endpoints: auth, customers, balances
│   └── data.py               # Deterministic in-memory synthetic data
├── tests/
│   ├── test_health.py
│   ├── test_auth.py
│   ├── test_customers.py
│   ├── test_balances.py
│   ├── test_contracts.py
│   └── schemas/              # JSON Schema contracts
├── utils/
│   ├── api_client.py         # requests wrapper + Allure request/response logging
│   └── schema_validator.py   # JSON Schema contract validation
├── conftest.py               # Fixtures: start/stop API, auth token, clients
├── scripts/                  # One-command demo runners
├── .github/workflows/ci.yml  # CI: install + run suite + upload Allure results
├── pytest.ini
└── requirements.txt
```

## Tech stack

- **Python 3.10+**, **pytest** (data-driven via parametrize)
- **requests** (HTTP), **jsonschema** (contract testing)
- **FastAPI** + **uvicorn** (self-contained system under test)
- **Allure** (reporting), **GitHub Actions** (CI)

## Related project

This framework validates the fictional **"Veridian"** platform at the
**API layer**. Its companion,
[**data-quality-framework**](https://github.com/d4tr3s14/data-quality-framework),
validates the same platform at the **data/warehouse layer** (BDD data-quality
and on-premise → cloud migration testing with behave + BigQuery/DuckDB).
Together they demonstrate end-to-end quality coverage.

## Notes

- All data and entities are **fictional and synthetic** — no real or proprietary
  data is included.
- The mock API exists to make the suite reproducible and to let tests trigger
  controlled error conditions (`401`/`404`/`422`) on demand.

## License

[MIT](LICENSE)
