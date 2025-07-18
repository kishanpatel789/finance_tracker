import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.api import app, create_engine, get_session
from src.models import SQLModel


@pytest.fixture(scope="function")
def db_engine(tmp_path):
    db_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_path}", echo=True)
    SQLModel.metadata.create_all(engine)

    yield engine

    engine.dispose()


@pytest.fixture(scope="function")
def test_session(db_engine):
    with Session(db_engine) as session:
        yield session


@pytest.fixture(name="client", scope="function")
def test_client(test_session: Session):
    def get_test_session():
        return test_session

    app.dependency_overrides[get_session] = get_test_session
    client = TestClient(app)

    yield client

    app.dependency_overrides.clear()


def test_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Finance Tracker is alive!"}


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


def test_add_category(client: TestClient, add_category):
    response = add_category
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == 1
    assert data["name"] == "Utilities"
    assert data["budget"] == "200.00"


def test_add_category_422(client: TestClient):
    payload = {}
    response = client.post("/categories", json=payload)

    assert response.status_code == 422


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
