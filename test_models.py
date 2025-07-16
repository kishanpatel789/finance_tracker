from datetime import datetime
import pytest
from sqlmodel import Session, create_engine

from models import SQLModel, Transaction, Category

engine = create_engine("sqlite:///:memory:", echo=True)


@pytest.fixture(scope="function", autouse=True)
def set_up_database():
    SQLModel.metadata.create_all(engine)


def test_create_category():
    category = Category(
            name="Utilities",
            budget=200,
            )

    with Session(engine) as session:
        session.add(category)
        session.commit()
        session.refresh(category)

    assert category.id is not None
    assert category.name == "Utilities"
    assert category.budget == 200

def test_create_transaction():
    category = Category(
            name="Utilities",
            budget=200,
            )
    transaction = Transaction(
            trans_date = datetime(2025, 6, 1, 15, 30, 0),
            amount = 50,
            vendor = "Amazon",
            note = "Handsoap",
            category=category,
            )
    with Session(engine) as session:
        session.add(category)
        session.add(transaction)
        session.commit()
        session.refresh(category)
        session.refresh(transaction)

    assert transaction.id is not None
    assert transaction.trans_date == datetime(2025, 6, 1, 15, 30, 0)
    assert transaction.amount == 50
    assert transaction.vendor == "Amazon"
    assert transaction.note == "Handsoap"
    assert transaction.created_at is not None
    assert transaction.category_id is not None
    assert transaction.category.name == "Utilities"




