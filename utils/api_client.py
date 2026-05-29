"""
Cliente HTTP delgado sobre ``requests`` para las pruebas de API.

Centraliza la URL base, la inyección del token Bearer y el registro de cada
request/response como evidencia en Allure. Mantener esto fuera de los tests
hace que los casos queden declarativos y legibles.
"""
from __future__ import annotations

import json
from typing import Any, Optional

import allure
import requests


class APIClient:
    def __init__(self, base_url: str, token: Optional[str] = None, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{path}"
        with allure.step(f"{method} {path}"):
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            _attach("Request", _format_request(method, url, kwargs))
            _attach("Response", _format_response(response))
            return response

    def get(self, path: str, **kwargs) -> requests.Response:
        return self._request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        return self._request("POST", path, **kwargs)

    def put(self, path: str, **kwargs) -> requests.Response:
        return self._request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        return self._request("DELETE", path, **kwargs)


def _attach(name: str, body: str) -> None:
    allure.attach(body, name=name, attachment_type=allure.attachment_type.TEXT)


def _format_request(method: str, url: str, kwargs: dict) -> str:
    lines = [f"{method} {url}"]
    if "params" in kwargs and kwargs["params"]:
        lines.append(f"Query params: {kwargs['params']}")
    if "json" in kwargs and kwargs["json"] is not None:
        lines.append("Body:\n" + json.dumps(kwargs["json"], indent=2, ensure_ascii=False))
    return "\n".join(lines)


def _format_response(response: requests.Response) -> str:
    lines = [f"HTTP {response.status_code} ({response.elapsed.total_seconds() * 1000:.0f} ms)"]
    try:
        lines.append(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except ValueError:
        lines.append(response.text)
    return "\n".join(lines)
