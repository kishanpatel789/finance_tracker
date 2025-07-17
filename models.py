from datetime import datetime, timezone
from decimal import Decimal

from sqlmodel import Column, Field, Numeric, Relationship, SQLModel


class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    budget: Decimal | None = Field(sa_column=Column(Numeric(10, 2)))

    transactions: list["Transaction"] = Relationship(back_populates="category")


class Transaction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    trans_date: datetime
    amount: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    vendor: str
    note: str | None = None
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime | None = None

    category_id: int | None = Field(
        default=None, foreign_key="category.id", ondelete="SET NULL"
    )
    category: Category | None = Relationship(
        back_populates="transactions",
        sa_relationship_kwargs={
            "lazy": "selectin",
        },
    )
