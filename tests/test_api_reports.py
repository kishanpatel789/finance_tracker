import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def add_categories(client: TestClient):
    categories = [
        {
            "name": "Utilities",
            "budget": 200.00,
        },
        {
            "name": "Travel",
        },
    ]
    for payload in categories:
        client.post("/categories", json=payload)


@pytest.fixture()
def add_transactions(client: TestClient, add_categories):
    transactions = [
        {
            "trans_date": "2025-07-14",
            "amount": 50.99,
            "vendor": "AT&T",
            "note": "Fiber Internet",
            "category_id": 1,
        },
        {
            "trans_date": "2025-07-31",
            "amount": 0.01,
            "vendor": "AT&T",
            "category_id": 1,
        },
        {
            "trans_date": "2025-07-01",
            "amount": 15.00,
            "vendor": "Expedia",
            "category_id": 2,
        },
        {
            "trans_date": "2025-07-01",
            "amount": 25.00,
            "vendor": "Amazon",
        },
        {
            "trans_date": "2025-06-02",
            "amount": 25.00,
            "vendor": "Amazon",
        },
    ]
    for payload in transactions:
        client.post("/transactions", json=payload)


def test_get_monthly_report(client: TestClient, add_transactions):
    response = client.get("/reports/monthly_budget?year_month=2025-07")
    data = response.json()

    assert response.status_code == 200

    assert data[0]["category_id"] == 1
    assert data[0]["category_name"] == "Utilities"
    assert data[0]["amount_spent"] == "51.00"
    assert data[0]["budget"] == "200.00"

    assert data[1]["category_id"] == 2
    assert data[1]["category_name"] == "Travel"
    assert data[1]["amount_spent"] == "15.00"
    assert data[1]["budget"] is None

    assert data[2]["category_id"] is None
    assert data[2]["category_name"] is None
    assert data[2]["amount_spent"] == "25.00"
    assert data[2]["budget"] is None


@pytest.mark.parametrize(
    "year_month,expected_error_type,expected_msg",
    [
        ("blah", "string_pattern_mismatch", "String should match pattern"),
        ("9999-12", "value_error", "cannot exceed current year"),
        ("2025-14", "value_error", "must be between '01' and '12'"),
    ],
)
def test_get_month_report_422_bad_param(
    client: TestClient, year_month, expected_error_type, expected_msg
):
    url = f"/reports/monthly_budget?year_month={year_month}"
    response = client.request("GET", url)
    data = response.json()
    assert response.status_code == 422
    assert data["detail"][0]["type"] == expected_error_type
    assert expected_msg in data["detail"][0]["msg"]
