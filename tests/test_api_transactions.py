import pytest
from fastapi.testclient import TestClient

from src.helpers import generate_url_query


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


@pytest.mark.parametrize(
    "method,url", [("POST", "/transactions"), ("PATCH", "/transactions/1")]
)
@pytest.mark.parametrize(
    "payload,expected_error_type",
    [
        (
            {
                "trans_date": "2024-07-14",
                "amount": 54.99,
                "vendor": "",
                "note": "",
            },
            "string_too_short",
        ),
        (
            {
                "trans_date": "2024-07-14",
                "amount": 54.99,
                "vendor": " " * 5,
                "note": " " * 5,
            },
            "string_too_short",
        ),
        (
            {
                "trans_date": "2024-07-14",
                "amount": 54.99,
                "vendor": "x" * 50,
                "note": "x" * 100,
            },
            "string_too_long",
        ),
    ],
)
def test_create_or_update_transaction_422_bad_strings(
    client: TestClient, add_transaction, method, url, payload, expected_error_type
):
    response = client.request(method, url, json=payload)
    data = response.json()
    assert response.status_code == 422
    assert data["detail"][0]["type"] == expected_error_type
    assert data["detail"][1]["type"] == expected_error_type


@pytest.mark.parametrize(
    "method,url", [("POST", "/transactions"), ("PATCH", "/transactions/1")]
)
@pytest.mark.parametrize(
    "payload,expected_error_type",
    [
        (
            {
                "trans_date": "2024-07-14",
                "amount": 1 * 10**9,
                "vendor": "AT&T",
            },
            "decimal_whole_digits",
        ),
        (
            {
                "trans_date": "2024-07-14",
                "amount": 1 * 10**11,
                "vendor": "AT&T",
            },
            "decimal_max_digits",
        ),
        (
            {
                "trans_date": "2024-07-14",
                "amount": 1.001,
                "vendor": "AT&T",
            },
            "decimal_max_places",
        ),
    ],
)
def test_create_or_update_transaction_422_bad_amount(
    client: TestClient, add_transaction, method, url, payload, expected_error_type
):
    response = client.request(method, url, json=payload)
    data = response.json()
    assert response.status_code == 422
    assert data["detail"][0]["type"] == expected_error_type


def test_get_transactions(client: TestClient, add_transaction, add_another_transaction):
    response = client.get("/transactions")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["trans_date"] == "2025-11-02"
    assert data[1]["trans_date"] == "2024-07-14"


@pytest.mark.parametrize(
    "term,expected_count",
    [("Utilities", 1), ("%20%20KrOgER%20", 1), ("DoesNotExist", 0)],
)
def test_get_transactions_search_by_term(
    client: TestClient, add_transaction, add_another_transaction, term, expected_count
):
    response = client.get(f"/transactions/?q={term}")
    data = response.json()
    assert response.status_code == 200
    assert len(data) == expected_count


@pytest.mark.parametrize(
    "start_date,end_date,expected_count",
    [("2024-01-01", "2024-12-31", 1), (None, "2024-12-31", 1), ("2025-01-01", None, 1)],
)
def test_get_transactions_search_by_date(
    client: TestClient,
    add_transaction,
    add_another_transaction,
    start_date,
    end_date,
    expected_count,
):
    url_query = generate_url_query({"start_date": start_date, "end_date": end_date})
    response = client.get(f"/transactions/?{url_query}")
    data = response.json()
    assert response.status_code == 200
    assert len(data) == expected_count


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
