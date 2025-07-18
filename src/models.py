from datetime import datetime, timezone
from decimal import Decimal

from pydantic import BaseModel
from sqlmodel import Column, Field, Numeric, Relationship, SQLModel


class CategoryBase(SQLModel):
    name: str
    budget: Decimal | None = Field(sa_column=Column(Numeric(10, 2)))


class Category(CategoryBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    transactions: list["Transaction"] = Relationship(back_populates="category")


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(SQLModel):
    name: str | None = None
    budget: Decimal | None = None


class CategoryRead(CategoryBase):
    id: int


class TransactionBase(SQLModel):
    trans_date: datetime
    amount: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    vendor: str
    note: str | None = None


class Transaction(TransactionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
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


class TransactionCreate(TransactionBase):
    pass


class TransactionRead(TransactionBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None
    category: CategoryBase


class DeleteResponse(BaseModel):
    detail: str
