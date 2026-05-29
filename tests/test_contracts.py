"""
Pruebas de contrato: validan la *forma* de las respuestas contra JSON Schema.

Detectan cambios incompatibles (campos renombrados/eliminados, tipos alterados)
independientemente de los valores concretos de los datos.
"""
import allure

from app import data
from utils.schema_validator import assert_matches_schema


@allure.feature("Contratos (JSON Schema)")
class TestContracts:

    @allure.title("La respuesta de /auth/token cumple el contrato")
    def test_token_contract(self, unauth_client):
        response = unauth_client.post("/auth/token", json={
            "client_id": data.DEMO_CLIENT_ID, "client_secret": data.DEMO_CLIENT_SECRET,
        })
        assert_matches_schema(response.json(), "token.json")

    @allure.title("La respuesta de detalle de cliente cumple el contrato")
    def test_customer_contract(self, client):
        response = client.get("/api/v1/customers/1")
        assert_matches_schema(response.json(), "customer.json")

    @allure.title("La respuesta del listado de clientes cumple el contrato")
    def test_customer_list_contract(self, client):
        response = client.get("/api/v1/customers")
        assert_matches_schema(response.json(), "customer_list.json")

    @allure.title("La respuesta de saldos cumple el contrato")
    def test_balances_contract(self, client):
        response = client.get("/api/v1/customers/1/balances")
        assert_matches_schema(response.json(), "balances.json")
