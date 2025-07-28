import pytest
from fastapi.testclient import TestClient

from src.api.dependencies import Session, create_engine, get_session
from src.api.main import app
from src.api.models import SQLModel


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
