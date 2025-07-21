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
def add_transaction(client: TestClient, add_category):
    payload = {
        "trans_date": "2024-07-14",
        "amount": 54.99,
        "vendor": "AT&T",
        "note": "Fiber Internet",
        "category_id": 1,
    }
    response = client.post("/transactions", json=payload)
    return response


@pytest.fixture()
def add_another_transaction(client: TestClient):
    payload = {
        "trans_date": "2025-11-02",
        "amount": 84.99,
        "vendor": "Kroger",
    }
    response = client.post("/transactions", json=payload)
    return response


def test_create_transaction(client: TestClient, add_transaction):
    response = add_transaction
    data = response.json()

    assert response.status_code == 201
    assert data["id"] == 1
    assert data["trans_date"] == "2024-07-14"
    assert data["amount"] == "54.99"
    assert data["vendor"] == "AT&T"
    assert data["note"] == "Fiber Internet"
    assert data["category"]["id"] == 1
    assert data["category"]["name"] == "Utilities"
    assert data["created_at"] is not None


def test_create_another_transaction(
    client: TestClient, add_transaction, add_another_transaction
):
    response = add_another_transaction
    data = response.json()

    assert response.status_code == 201
    assert data["id"] == 2
    assert data["trans_date"] == "2025-11-02"
    assert data["amount"] == "84.99"
    assert data["vendor"] == "Kroger"
    assert data["note"] is None
    assert data["category"] is None
    assert data["created_at"] is not None


def test_create_transaction_invalid_category(client: TestClient):
    payload = {
        "trans_date": "2025-11-02",
        "amount": 84.99,
        "vendor": "Kroger",
        "category_id": 99,
    }
    response = client.post("/transactions", json=payload)
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == "Category not found"


def test_create_transaction_422(client: TestClient):
    payload = {}
    response = client.post("/transactions", json=payload)

    assert response.status_code == 422


def test_get_transactions(client: TestClient, add_transaction, add_another_transaction):
    response = client.get("/transactions")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2


def test_get_transaction(client: TestClient, add_transaction):
    response = client.get("/transactions/1")
    data = response.json()

    assert data["id"] == 1
    assert data["trans_date"] == "2024-07-14"
    assert data["amount"] == "54.99"
    assert data["vendor"] == "AT&T"
    assert data["note"] == "Fiber Internet"
    assert data["category"]["id"] == 1
    assert data["category"]["name"] == "Utilities"


def test_get_transaction_not_found(client: TestClient):
    response = client.get("/transactions/99")
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == "Transaction not found"


def test_update_transaction(client: TestClient, add_category, add_another_transaction):
    payload = {
        "amount": "100.00",
        "note": "i needed it",
        "vendor": "Amazon",
        "category_id": 1,
    }
    response = client.patch("/transactions/1", json=payload)
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == 1
    assert data["trans_date"] == "2025-11-02"
    assert data["amount"] == "100.00"
    assert data["vendor"] == "Amazon"
    assert data["note"] == "i needed it"
    assert data["category"]["id"] == 1
    assert data["category"]["name"] == "Utilities"
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


def test_update_transaction_invalid_category(
    client: TestClient, add_another_transaction
):
    payload = {
        "category_id": 99,
    }
    response = client.patch("/transactions/1", json=payload)
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == "Category not found"


def test_update_transaction_not_found(client: TestClient):
    response = client.patch("/transactions/99", json={})
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == "Transaction not found"


def test_delete_transaction(client: TestClient, add_transaction):
    response = client.delete("/transactions/1")
    data = response.json()

    assert response.status_code == 200
    assert data["detail"] == "Transaction with ID 1 deleted successfully"

    response = client.get("/transactions/1")

    assert response.status_code == 404


def test_delete_transaction_not_found(client: TestClient):
    response = client.delete("/transactions/99")
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == "Transaction not found"
