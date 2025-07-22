import re
from datetime import date, datetime, timezone
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator
from sqlmodel import Field, Relationship, SQLModel


class MySQLModel(SQLModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )


class CategoryBase(MySQLModel):
    name: str = Field(min_length=3, max_length=25)
    budget: Decimal | None = Field(max_digits=10, decimal_places=2, default=None)

    @field_validator("name", mode="before")
    @classmethod
    def standardize_name(cls, value: str) -> str:
        value = re.sub(r"\s+", " ", value)
        value = value.title()
        return value


class Category(CategoryBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    transactions: list["Transaction"] = Relationship(back_populates="category")


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(MySQLModel):
    name: str | None = Field(min_length=3, max_length=25, default=None)
    budget: Decimal | None = Field(max_digits=10, decimal_places=2, default=None)

    @field_validator("name", mode="before")
    @classmethod
    def standardize_name(cls, value: str) -> str:
        value = re.sub(r"\s+", " ", value)
        value = value.title()
        return value


class CategoryRead(CategoryBase):
    id: int
    budget: Decimal | None = Field(max_digits=10, decimal_places=2)


class CategoryReadNested(MySQLModel):
    id: int
    name: str


class TransactionBase(MySQLModel):
    trans_date: date
    amount: Decimal = Field(max_digits=10, decimal_places=2)
    vendor: str = Field(min_length=3, max_length=25)
    note: str | None = Field(min_length=1, max_length=50, default=None)


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
    category_id: int | None = None


class TransactionUpdate(MySQLModel):
    trans_date: datetime | None = None
    amount: Decimal | None = Field(max_digits=10, decimal_places=2, default=None)
    vendor: str | None = Field(min_length=3, max_length=25, default=None)
    note: str | None = Field(min_length=1, max_length=25, default=None)
    category_id: int | None = None


class TransactionRead(TransactionBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None
    category: CategoryReadNested | None = None


class DeleteResponse(BaseModel):
    detail: str
