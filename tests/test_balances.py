"""Pruebas del recurso de saldos, incluyendo una validación de regla de negocio."""
import allure
import pytest


@allure.feature("Saldos")
class TestBalances:

    @allure.story("Consulta")
    @allure.title("Obtener los saldos de un cliente existente")
    def test_get_balances(self, client):
        response = client.get("/api/v1/customers/1/balances")
        assert response.status_code == 200
        body = response.json()
        assert body["customer_id"] == 1
        assert isinstance(body["balances"], list)
        for b in body["balances"]:
            assert b["fund"] in {"A", "B", "C", "D", "E"}
            assert b["balance_clp"] >= 0

    @allure.story("Regla de negocio")
    @allure.title("La distribución porcentual de los saldos suma 100%")
    @pytest.mark.parametrize("customer_id", [1, 5, 10, 15])
    def test_share_distribution_sums_100(self, client, customer_id):
        response = client.get(f"/api/v1/customers/{customer_id}/balances")
        assert response.status_code == 200
        balances = response.json()["balances"]
        if balances:  # algunos clientes podrían no tener saldos
            total_pct = sum(b["share_pct"] for b in balances)
            assert abs(total_pct - 100.0) <= 0.1, f"La distribución suma {total_pct}%, no 100%."

    @allure.story("Consulta")
    @allure.title("Obtener saldos de un cliente inexistente devuelve 404")
    def test_balances_unknown_customer_returns_404(self, client):
        response = client.get("/api/v1/customers/999999/balances")
        assert response.status_code == 404
