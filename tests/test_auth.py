"""Pruebas de autenticación: token válido y casos negativos de seguridad."""
import allure
import pytest

from app import data


@allure.feature("Autenticación")
class TestAuthentication:

    @allure.story("Token válido")
    @allure.title("Credenciales correctas devuelven un token Bearer")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_valid_credentials_return_token(self, unauth_client):
        response = unauth_client.post("/auth/token", json={
            "client_id": data.DEMO_CLIENT_ID,
            "client_secret": data.DEMO_CLIENT_SECRET,
        })
        assert response.status_code == 200
        body = response.json()
        assert body["token_type"] == "bearer"
        assert len(body["access_token"]) > 0
        assert body["expires_in"] > 0

    @allure.story("Credenciales inválidas")
    @allure.title("Credenciales incorrectas devuelven 401")
    @pytest.mark.parametrize("client_id,client_secret", [
        (data.DEMO_CLIENT_ID, "secreto-incorrecto"),
        ("cliente-inexistente", data.DEMO_CLIENT_SECRET),
        ("cliente-inexistente", "secreto-incorrecto"),
    ])
    def test_invalid_credentials_return_401(self, unauth_client, client_id, client_secret):
        response = unauth_client.post("/auth/token", json={
            "client_id": client_id, "client_secret": client_secret,
        })
        assert response.status_code == 401

    @allure.story("Cuerpo inválido")
    @allure.title("Cuerpo mal formado en /auth/token devuelve 422")
    @pytest.mark.parametrize("body", [
        {"client_id": "solo-id"},                       # falta client_secret
        {"client_secret": "solo-secret"},               # falta client_id
        {"client_id": "", "client_secret": ""},         # vacíos (min_length=1)
        {},                                             # cuerpo vacío
    ])
    def test_malformed_body_returns_422(self, unauth_client, body):
        response = unauth_client.post("/auth/token", json=body)
        assert response.status_code == 422

    @allure.story("Acceso protegido")
    @allure.title("Acceder a un recurso protegido sin token devuelve 401")
    def test_protected_resource_without_token_returns_401(self, unauth_client):
        response = unauth_client.get("/api/v1/customers")
        assert response.status_code == 401

    @allure.story("Acceso protegido")
    @allure.title("Acceder con un token inválido devuelve 401")
    def test_protected_resource_with_invalid_token_returns_401(self, base_url):
        from utils.api_client import APIClient

        bogus = APIClient(base_url, token="token-falso-123")
        response = bogus.get("/api/v1/customers")
        assert response.status_code == 401
