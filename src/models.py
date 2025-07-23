import re
from datetime import date, datetime, timezone
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator
from sqlmodel import Field, Relationship, SQLModel


class MySQLModel(SQLModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )


field_money_dec_or_none = Field(max_digits=10, decimal_places=2, default=None)
field_money_dec = Field(max_digits=10, decimal_places=2)
field_str_1_25_or_none = Field(min_length=1, max_length=25, default=None)
field_str_1_25 = Field(min_length=1, max_length=25)


class CategoryBase(MySQLModel):
    name: str = field_str_1_25
    budget: Decimal | None = field_money_dec_or_none

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


class CategoryUpdate(CategoryBase):
    name: str | None = field_str_1_25_or_none


class CategoryRead(CategoryBase):
    id: int


class CategoryReadNested(MySQLModel):
    id: int
    name: str


class TransactionBase(MySQLModel):
    trans_date: date
    amount: Decimal = field_money_dec
    vendor: str = field_str_1_25
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


class TransactionUpdate(TransactionBase):
    trans_date: datetime | None = None
    amount: Decimal | None = field_money_dec_or_none
    vendor: str | None = field_str_1_25_or_none

    category_id: int | None = None


class TransactionRead(TransactionBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None
    category: CategoryReadNested | None = None


class DeleteResponse(BaseModel):
    detail: str


class PaginationInput(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=25, ge=1, le=50)
