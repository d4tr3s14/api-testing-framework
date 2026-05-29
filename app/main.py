"""
API REST de demostración: plataforma de inversión ficticia "Veridian".

Es el *sistema bajo prueba* (SUT) del framework. Se ejecuta localmente, por lo
que la suite de pruebas no depende de ningún servicio externo y es totalmente
reproducible (igual que el backend DuckDB del proyecto data-quality-framework).

Expone autenticación por token Bearer, recursos paginados, validación de
cuerpo (422) y errores controlados (401/404), pensados para ejercitar pruebas
positivas, negativas, de borde y de contrato.
"""
from __future__ import annotations

import uuid
from enum import Enum
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query, status
from pydantic import BaseModel, Field

from app import data

app = FastAPI(title="Veridian Investment API", version="1.0.0")

# Tokens emitidos en esta ejecución (almacén en memoria del mock).
_ISSUED_TOKENS: set[str] = set()


# --------------------------- Modelos ---------------------------------------
class Segment(str, Enum):
    RETAIL = "RETAIL"
    PREMIUM = "PREMIUM"
    PRIVATE = "PRIVATE"


class TokenRequest(BaseModel):
    client_id: str = Field(..., min_length=1)
    client_secret: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


class Customer(BaseModel):
    id: int
    full_name: str
    email: str
    segment: Segment
    status: str


class CustomerCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=80)
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    segment: Segment


class Balance(BaseModel):
    fund: str
    balance_clp: float
    share_pct: float


class CustomerBalances(BaseModel):
    customer_id: int
    balances: list[Balance]


class CustomerList(BaseModel):
    items: list[Customer]
    total: int
    limit: int
    offset: int


# --------------------------- Seguridad -------------------------------------
def require_auth(authorization: Optional[str] = Header(default=None)):
    """Valida el token Bearer. Devuelve 401 si falta o es inválido."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta el token de autenticación.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ", 1)[1].strip()
    if token not in _ISSUED_TOKENS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


# --------------------------- Endpoints -------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/token", response_model=TokenResponse)
def issue_token(body: TokenRequest):
    if body.client_id != data.DEMO_CLIENT_ID or body.client_secret != data.DEMO_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas.",
        )
    token = uuid.uuid4().hex
    _ISSUED_TOKENS.add(token)
    return TokenResponse(access_token=token)


@app.get("/api/v1/customers", response_model=CustomerList)
def list_customers(
    segment: Optional[Segment] = None,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: str = Depends(require_auth),
):
    items = list(data.CUSTOMERS.values())
    if segment:
        items = [c for c in items if c["segment"] == segment.value]
    total = len(items)
    page = items[offset: offset + limit]
    return {"items": page, "total": total, "limit": limit, "offset": offset}


@app.get("/api/v1/customers/{customer_id}", response_model=Customer)
def get_customer(customer_id: int, _: str = Depends(require_auth)):
    customer = data.CUSTOMERS.get(customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Cliente {customer_id} no encontrado.")
    return customer


@app.post("/api/v1/customers", response_model=Customer, status_code=status.HTTP_201_CREATED)
def create_customer(body: CustomerCreate, _: str = Depends(require_auth)):
    return data.add_customer(body.full_name, body.email, body.segment.value)


@app.get("/api/v1/customers/{customer_id}/balances", response_model=CustomerBalances)
def get_balances(customer_id: int, _: str = Depends(require_auth)):
    if customer_id not in data.CUSTOMERS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Cliente {customer_id} no encontrado.")
    return {"customer_id": customer_id, "balances": data.BALANCES.get(customer_id, [])}
