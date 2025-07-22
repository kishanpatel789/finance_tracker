import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def add_category(client: TestClient):
    payload = {
        "name": "Utilities",
        "budget": 200.00,
    }
    response = client.post("/categories", json=payload)
    return response


@pytest.fixture()
def add_another_category(client: TestClient):
    payload = {
        "name": "General",
        "budget": 150.00,
    }
    response = client.post("/categories", json=payload)
    return response


def test_create_category(client: TestClient, add_category):
    response = add_category
    data = response.json()

    assert response.status_code == 201
    assert data["id"] == 1
    assert data["name"] == "Utilities"
    assert data["budget"] == "200.00"


def test_create_category_standardize_name(client: TestClient):
    payload = {
        "name": "   food  and drINK  ",
        "budget": None,
    }
    response = client.post("/categories", json=payload)
    data = response.json()

    assert response.status_code == 201
    assert data["id"] == 1
    assert data["name"] == "Food And Drink"
    assert data["budget"] is None


def test_create_category_422_empty_payload(client: TestClient):
    payload = {}
    response = client.post("/categories", json=payload)

    assert response.status_code == 422


@pytest.mark.parametrize(
    "method,url", [("POST", "/categories"), ("PATCH", "/categories/1")]
)
def test_create_or_update_category_422_bad_strings(
    client: TestClient, add_category, method, url
):
    payload = {"name": ""}
    response = client.request(method, url, json=payload)
    data = response.json()
    assert response.status_code == 422
    assert data["detail"][0]["type"] == "string_too_short"

    payload = {"name": " " * 5}
    response = client.request(method, url, json=payload)
    data = response.json()
    assert response.status_code == 422
    assert data["detail"][0]["type"] == "string_too_short"

    payload = {"name": "x" * 50}
    response = client.request(method, url, json=payload)
    data = response.json()
    assert response.status_code == 422
    assert data["detail"][0]["type"] == "string_too_long"


@pytest.mark.parametrize(
    "method,url", [("POST", "/categories"), ("PATCH", "/categories/1")]
)
def test_create_or_update_category_422_bad_amount(
    client: TestClient, add_category, method, url
):
    payload = {"name": "Test Category", "budget": 1 * 10**9}
    response = client.request(method, url, json=payload)
    data = response.json()
    assert response.status_code == 422
    assert data["detail"][0]["type"] == "decimal_whole_digits"

    payload = {"name": "Test Category", "budget": 1 * 10**11}
    response = client.request(method, url, json=payload)
    data = response.json()
    assert response.status_code == 422
    assert data["detail"][0]["type"] == "decimal_max_digits"

    payload = {"name": "Test Category", "budget": 1.001}
    response = client.request(method, url, json=payload)
    data = response.json()
    assert response.status_code == 422
    assert data["detail"][0]["type"] == "decimal_max_places"


def test_create_duplicate_category(client: TestClient, add_category):
    payload = {"name": "Utilities", "budget": None}
    response = client.post("/categories", json=payload)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_get_categories(client: TestClient, add_category, add_another_category):
    response = client.get("/categories")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2


def test_get_category(client: TestClient, add_category):
    response = client.get("/categories/1")
    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "Utilities"
    assert data["budget"] == "200.00"


def test_get_category_not_found(client: TestClient):
    response = client.get("/categories/99")
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == "Category not found"


def test_update_category(client: TestClient, add_category):
    payload = {
        "name": "Updated Utilities",
    }
    response = client.patch("/categories/1", json=payload)
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == 1
    assert data["name"] == "Updated Utilities"
    assert data["budget"] == "200.00"


def test_update_category_conflicting_name(
    client: TestClient, add_category, add_another_category
):
    payload = {"name": "Utilities", "budget": None}
    response = client.patch("/categories/2", json=payload)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_update_category_standardize_name(client: TestClient, add_category):
    payload = {
        "name": "   food  and drINK  ",
        "budget": None,
    }
    response = client.patch("/categories/1", json=payload)
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == 1
    assert data["name"] == "Food And Drink"
    assert data["budget"] is None


@pytest.mark.focus()
def test_update_category_update_budget(client: TestClient, add_category):
    """Test existing category can update budget without aggressive validation."""
    payload = {
        "name": "Utilities",
        "budget": 100.00,
    }
    response = client.patch("/categories/1", json=payload)
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == 1
    assert data["name"] == "Utilities"
    assert data["budget"] == "100.00"


def test_update_category_not_found(client: TestClient):
    response = client.patch("/categories/99", json={})
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == "Category not found"


def test_delete_category(client: TestClient, add_category):
    response = client.delete("/categories/1")
    data = response.json()

    assert response.status_code == 200
    assert data["detail"] == "Category with ID 1 deleted successfully"

    response = client.get("/categories/1")

    assert response.status_code == 404


def test_delete_category_not_found(client: TestClient):
    response = client.delete("/categories/99")
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == "Category not found"
