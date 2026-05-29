"""
Fixtures de sesión: levantan la API real localmente y proveen clientes HTTP.

La API (``app.main``) se ejecuta en un hilo con uvicorn sobre un puerto libre.
Las pruebas la consumen por HTTP real con ``requests`` (no in-process), igual
que contra un servicio desplegado. Al terminar la sesión, el servidor se apaga.
"""
from __future__ import annotations

import socket
import threading
import time

import pytest
import requests
import uvicorn

from app import data
from app.main import app


def _free_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.fixture(scope="session")
def base_url():
    """Levanta la API de prueba y devuelve su URL base."""
    port = _free_port()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    server.install_signal_handlers = lambda: None  # requerido fuera del hilo principal

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    url = f"http://127.0.0.1:{port}"
    deadline = time.time() + 15
    while time.time() < deadline:
        try:
            if requests.get(f"{url}/health", timeout=0.5).status_code == 200:
                break
        except requests.RequestException:
            time.sleep(0.1)
    else:
        raise RuntimeError("La API de prueba no respondió a tiempo.")

    yield url

    server.should_exit = True
    thread.join(timeout=5)


@pytest.fixture(scope="session")
def auth_token(base_url):
    """Obtiene un token Bearer válido desde el endpoint de autenticación."""
    resp = requests.post(
        f"{base_url}/auth/token",
        json={"client_id": data.DEMO_CLIENT_ID, "client_secret": data.DEMO_CLIENT_SECRET},
        timeout=10,
    )
    assert resp.status_code == 200, f"No se pudo obtener token: {resp.text}"
    return resp.json()["access_token"]


@pytest.fixture
def client(base_url, auth_token):
    """Cliente HTTP autenticado (token Bearer inyectado)."""
    from utils.api_client import APIClient

    return APIClient(base_url, token=auth_token)


@pytest.fixture
def unauth_client(base_url):
    """Cliente HTTP sin autenticación (para pruebas negativas de seguridad)."""
    from utils.api_client import APIClient

    return APIClient(base_url)


@pytest.fixture(autouse=True)
def _reset_state():
    """Restaura los datos en memoria antes de cada prueba para aislarlas."""
    data.reset_state()
    yield
