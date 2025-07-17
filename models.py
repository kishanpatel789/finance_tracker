from datetime import datetime, timezone

from sqlmodel import Field, Relationship, SQLModel


class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    budget: float

    transactions: list["Transaction"] = Relationship(back_populates="category")


class Transaction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    trans_date: datetime
    amount: float
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
