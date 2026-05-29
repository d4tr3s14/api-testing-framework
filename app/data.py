"""
Datos sintéticos en memoria para la API de demostración.

Modela clientes de la plataforma ficticia de inversión multifondo "Veridian"
y sus saldos por fondo (A-E). Todos los datos son inventados y deterministas;
no proviene ningún dato de ningún cliente real.

Es la contraparte a nivel de API del proyecto `data-quality-framework`, que
valida los mismos conceptos a nivel de base de datos.
"""
from __future__ import annotations

import random

SEGMENTS = ["RETAIL", "PREMIUM", "PRIVATE"]
FUNDS = ["A", "B", "C", "D", "E"]

# Credenciales de la API de demo (ficticias, solo para el mock local).
DEMO_CLIENT_ID = "veridian-demo"
DEMO_CLIENT_SECRET = "demo-secret"


def _seed_customers():
    rng = random.Random(42)
    customers = {}
    balances = {}
    first = ["Ana", "Bruno", "Carla", "Diego", "Elena", "Felipe", "Gloria",
             "Hugo", "Ines", "Javier", "Karen", "Luis", "Marta", "Nestor", "Olga"]
    last = ["Rojas", "Soto", "Vega", "Munoz", "Castro", "Pinto", "Araya",
            "Bravo", "Cortes", "Diaz", "Fuentes", "Gomez", "Herrera"]

    for cid in range(1, 16):
        name = f"{rng.choice(first)} {rng.choice(last)}"
        email = f"cliente{cid}@veridian.example"
        segment = rng.choice(SEGMENTS)
        customers[cid] = {
            "id": cid,
            "full_name": name,
            "email": email,
            "segment": segment,
            "status": "ACTIVE",
        }

        # Saldos por fondo (subconjunto aleatorio de fondos por cliente).
        client_funds = rng.sample(FUNDS, rng.randint(1, 4))
        raw = {f: round(rng.uniform(1_000_000, 90_000_000), 0) for f in client_funds}
        total = sum(raw.values())
        balances[cid] = [
            {"fund": f, "balance_clp": amount,
             "share_pct": round(amount / total * 100, 2)}
            for f, amount in sorted(raw.items())
        ]

    return customers, balances


CUSTOMERS, BALANCES = _seed_customers()
_NEXT_ID = max(CUSTOMERS) + 1


def reset_state():
    """Restaura el estado en memoria (útil entre ejecuciones de prueba)."""
    global CUSTOMERS, BALANCES, _NEXT_ID
    CUSTOMERS, BALANCES = _seed_customers()
    _NEXT_ID = max(CUSTOMERS) + 1


def add_customer(full_name: str, email: str, segment: str) -> dict:
    global _NEXT_ID
    new = {
        "id": _NEXT_ID,
        "full_name": full_name,
        "email": email,
        "segment": segment,
        "status": "ACTIVE",
    }
    CUSTOMERS[_NEXT_ID] = new
    BALANCES[_NEXT_ID] = []
    _NEXT_ID += 1
    return new
