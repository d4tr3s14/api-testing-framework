# Architecture

## Design goals

1. **Self-contained.** The system under test (a FastAPI app) ships with the
   tests and runs locally, so the suite needs no external services and is fully
   reproducible — clone, install, `pytest`.
2. **Real HTTP.** Tests hit the API over `localhost` with `requests`, exactly
   like they would against a deployed service (not in-process shortcuts).
3. **Layered coverage.** Functional (positive/negative/boundary), security
   (auth), and contract (JSON Schema) checks, all reported in Allure.

## Components

```
                    pytest  (test runner)
                      │
        ┌─────────────┼─────────────────────────┐
        │             │                          │
   conftest.py    tests/*.py                utils/
   (fixtures)    (test cases)        ┌───────────┴───────────┐
        │                            │                       │
        │                       api_client.py        schema_validator.py
        │                       (requests wrapper)   (JSON Schema contracts)
        │
        ▼  starts in a thread (uvicorn, free port)
   app/main.py  ── FastAPI "Veridian Investment API" (system under test)
   app/data.py  ── deterministic in-memory synthetic data
```

## Fixture lifecycle (`conftest.py`)

- `base_url` *(session)* — picks a free port, starts the API with uvicorn in a
  daemon thread, polls `/health` until ready, yields the URL, and shuts the
  server down on teardown.
- `auth_token` *(session)* — performs the OAuth-style token exchange once.
- `client` / `unauth_client` *(function)* — authenticated and anonymous
  `APIClient` instances.
- `_reset_state` *(autouse)* — restores the in-memory dataset before each test
  so cases are independent (e.g. creating a customer doesn't affect counts).

## Test categories

| File | Category | Examples |
|---|---|---|
| `test_health.py` | Smoke | service liveness |
| `test_auth.py` | Security / negative | valid token, 401 on bad creds, 401 without/invalid token, 422 on malformed body |
| `test_customers.py` | Functional / boundary | listing, pagination limits, segment filter, 404, 201 create, 422 validation |
| `test_balances.py` | Functional / business rule | balances retrieval, share distribution sums 100% |
| `test_contracts.py` | Contract | responses validated against JSON Schema |

## Why a mock API instead of a public one

Hitting a public API (e.g. JSONPlaceholder) makes a suite flaky and
non-deterministic: network failures, rate limits, and unannounced changes break
CI for reasons unrelated to the code. Shipping the SUT guarantees the suite is
deterministic and demonstrates the full testing lifecycle, including controlled
error conditions (401/404/422) that public APIs rarely let you trigger on demand.

## Companion project

This is the **API-layer** counterpart to
[`data-quality-framework`](https://github.com/d4tr3s14/data-quality-framework),
which validates the same fictional "Veridian" platform at the **data/warehouse
layer**. Together they show end-to-end quality coverage: the data that lands in
the warehouse and the API that exposes it.
