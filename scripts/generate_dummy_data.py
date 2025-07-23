import random
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from faker import Faker
from sqlmodel import Session, create_engine

from src.models import Category, SQLModel, Transaction

fake = Faker()
random.seed(42)
Faker.seed(42)


def random_date_within_last_year() -> date:
    days_ago = random.randint(0, 365)
    return (datetime.now(timezone.utc) - timedelta(days=days_ago)).date()


def generate_categories() -> list[Category]:
    category_names = [
        "Groceries",
        "Rent",
        "Utilities",
        "Restaurant",
        "Business Miscallaneous",
        "General Merchandise",
        "Insurance",
        "Gas/Fuel",
        "Automotive",
        "Subscriptions",
    ]
    categories = []
    for name in category_names:
        budget = round(random.uniform(50, 2000), 2)
        categories.append(Category(name=name, budget=Decimal(budget)))
    return categories


def generate_transactions(categories: list[Category], n=250) -> list[Transaction]:
    transactions = []
    for _ in range(n):
        amount = round(random.uniform(5, 300), 2)
        trans = Transaction(
            trans_date=random_date_within_last_year(),
            amount=Decimal(amount),
            vendor=fake.company()[:25],
            note=fake.sentence(nb_words=6)[:50],
            category_id=random.choice(categories).id if categories else None,
        )
        transactions.append(trans)
    return transactions


def get_engine():
    engine = create_engine("sqlite:///finance_tracker.sqlite", echo=False)
    return engine


def create_db_and_tables(engine):
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def generate_data(engine):
    with Session(engine) as session:
        categories = generate_categories()
        for cat in categories:
            session.add(cat)
        session.commit()

        for cat in categories:
            session.refresh(cat)

        transactions = generate_transactions(categories)
        for t in transactions:
            session.add(t)
        session.commit()

        print(
            f"Generated {len(categories)} categories and {len(transactions)} transactions"
        )


def main():
    engine = get_engine()
    create_db_and_tables(engine)
    generate_data(engine)


if __name__ == "__main__":
    main()
