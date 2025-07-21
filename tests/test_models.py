from datetime import date

import pytest
from sqlmodel import Session, create_engine

from src.models import Category, SQLModel, Transaction


@pytest.fixture(scope="function")
def db_engine():
    engine = create_engine("sqlite:///:memory:", echo=True)
    SQLModel.metadata.create_all(engine)

    yield engine

    engine.dispose()


@pytest.fixture(scope="function")
def session(db_engine):
    with Session(db_engine) as session:
        yield session


def test_create_category(session):
    category = Category(
        name="Utilities",
        budget=200,
    )

    session.add(category)
    session.commit()
    session.refresh(category)

    assert category.id == 1
    assert category.name == "Utilities"
    assert category.budget == 200


def test_create_transaction(session):
    category = Category(
        name="General",
        budget=200,
    )
    transaction = Transaction(
        trans_date=date(2025, 6, 1),
        amount=50,
        vendor="Amazon",
        note="Handsoap",
        category=category,
    )
    session.add(category)
    session.add(transaction)
    session.commit()
    session.refresh(category)
    session.refresh(transaction)

    assert transaction.id == 1
    assert transaction.trans_date == date(2025, 6, 1)
    assert transaction.amount == 50
    assert transaction.vendor == "Amazon"
    assert transaction.note == "Handsoap"
    assert transaction.created_at is not None
    assert transaction.category_id is not None
    assert transaction.category.name == "General"
