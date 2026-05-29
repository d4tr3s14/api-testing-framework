"""Smoke test del endpoint de salud (sin autenticación)."""
import allure


@allure.feature("Servicio")
@allure.story("Health check")
@allure.title("GET /health responde 200 y estado ok")
def test_health_ok(unauth_client):
    response = unauth_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
