"""Pruebas del recurso de clientes: listado, paginación, filtros, detalle y creación."""
import allure
import pytest

TOTAL_CUSTOMERS = 15  # clientes sembrados de forma determinista


@allure.feature("Clientes")
class TestListCustomers:

    @allure.story("Listado")
    @allure.title("El listado por defecto devuelve la primera página")
    def test_default_listing(self, client):
        response = client.get("/api/v1/customers")
        assert response.status_code == 200
        body = response.json()
        assert body["total"] == TOTAL_CUSTOMERS
        assert body["limit"] == 10
        assert body["offset"] == 0
        assert len(body["items"]) == 10

    @allure.story("Paginación")
    @allure.title("La paginación respeta limit y offset")
    @pytest.mark.parametrize("limit,offset,expected_len", [
        (5, 0, 5),
        (10, 10, 5),
        (5, 13, 2),
        (100, 0, TOTAL_CUSTOMERS),
    ])
    def test_pagination(self, client, limit, offset, expected_len):
        response = client.get("/api/v1/customers", params={"limit": limit, "offset": offset})
        assert response.status_code == 200
        assert len(response.json()["items"]) == expected_len

    @allure.story("Paginación")
    @allure.title("Parámetros de paginación fuera de rango devuelven 422")
    @pytest.mark.parametrize("params", [
        {"limit": 0},      # ge=1
        {"limit": 101},    # le=100
        {"offset": -1},    # ge=0
    ])
    def test_pagination_out_of_range_returns_422(self, client, params):
        response = client.get("/api/v1/customers", params=params)
        assert response.status_code == 422

    @allure.story("Filtros")
    @allure.title("El filtro por segmento solo devuelve ese segmento")
    @pytest.mark.parametrize("segment", ["RETAIL", "PREMIUM", "PRIVATE"])
    def test_filter_by_segment(self, client, segment):
        response = client.get("/api/v1/customers", params={"segment": segment, "limit": 100})
        assert response.status_code == 200
        items = response.json()["items"]
        assert all(c["segment"] == segment for c in items)


@allure.feature("Clientes")
class TestGetCustomer:

    @allure.story("Detalle")
    @allure.title("Obtener un cliente existente devuelve sus datos")
    def test_get_existing_customer(self, client):
        response = client.get("/api/v1/customers/1")
        assert response.status_code == 200
        assert response.json()["id"] == 1

    @allure.story("Detalle")
    @allure.title("Obtener un cliente inexistente devuelve 404")
    def test_get_unknown_customer_returns_404(self, client):
        response = client.get("/api/v1/customers/999999")
        assert response.status_code == 404


@allure.feature("Clientes")
class TestCreateCustomer:

    @allure.story("Creación")
    @allure.title("Crear un cliente válido devuelve 201 con el recurso creado")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_valid_customer(self, client):
        payload = {"full_name": "Patricia Núñez", "email": "patricia@veridian.example",
                   "segment": "PREMIUM"}
        response = client.post("/api/v1/customers", json=payload)
        assert response.status_code == 201
        body = response.json()
        assert body["id"] > TOTAL_CUSTOMERS
        assert body["full_name"] == payload["full_name"]
        assert body["segment"] == "PREMIUM"
        assert body["status"] == "ACTIVE"

    @allure.story("Creación")
    @allure.title("Crear un cliente con cuerpo inválido devuelve 422")
    @pytest.mark.parametrize("payload", [
        {"full_name": "A", "email": "a@b.com", "segment": "RETAIL"},          # nombre muy corto
        {"full_name": "Nombre Valido", "email": "no-es-email", "segment": "RETAIL"},  # email inválido
        {"full_name": "Nombre Valido", "email": "a@b.com", "segment": "GOLD"},  # segmento inexistente
        {"email": "a@b.com", "segment": "RETAIL"},                            # falta full_name
    ])
    def test_create_invalid_customer_returns_422(self, client, payload):
        response = client.post("/api/v1/customers", json=payload)
        assert response.status_code == 422
