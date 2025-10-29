import re
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import StrEnum
from typing import Annotated

from fastapi import Query
from pydantic import BaseModel, ConfigDict, HttpUrl, field_validator
from sqlalchemy import Column
from sqlalchemy import Enum as SaEnum
from sqlmodel import Field, Relationship, SQLModel


class PaginationInput(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=25, ge=1, le=50)


class TransactionQueryParams(BaseModel):
    q: Annotated[str | None, Query(max_length=40)] = None
    start_date: date | None = None
    end_date: date | None = None


class PageLinks(BaseModel):
    current: HttpUrl
    prev: HttpUrl | None = None
    next: HttpUrl | None = None


class PageBase(BaseModel):
    data: list
    total_row_count: int
    total_page_count: int
    links: PageLinks


class MySQLModel(SQLModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )


OptionalMoneyField = Field(max_digits=10, decimal_places=2, default=None)
MoneyField = Field(max_digits=10, decimal_places=2)
OptionalStringField = Field(min_length=1, max_length=25, default=None)
StringField = Field(min_length=1, max_length=25)


class CategoryBase(MySQLModel):
    name: str = StringField
    budget: Decimal | None = OptionalMoneyField

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
    name: str | None = OptionalStringField

    @field_validator("name", mode="before")
    @classmethod
    def reject_null_name(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("Field 'name' cannot be null")
        return value


class CategoryRead(CategoryBase):
    id: int


class CategoryReadNested(MySQLModel):
    id: int
    name: str


def enum_column(enum_cls):
    """A SQLAlchemy column that properly returns ENUM values instead of labels"""
    return Column(SaEnum(enum_cls, values_callable=lambda x: [e.value for e in x]))


class AccountTypeEnum(StrEnum):
    CASH = "cash"
    CREDIT_CARD = "credit_card"


class AccountBase(MySQLModel):
    name: str = StringField
    active: bool = True
    short_number: str = StringField
    account_type: AccountTypeEnum = Field(sa_column=enum_column(AccountTypeEnum))


class Account(AccountBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    transactions: list["Transaction"] = Relationship(back_populates="account")


class AccountCreate(AccountBase):
    pass


class AccountUpdate(AccountBase):
    name: str | None = OptionalStringField
    active: bool | None
    short_number: str | None
    account_type: AccountTypeEnum | None

    @field_validator("name", mode="before")
    @classmethod
    def reject_null_name(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("Field 'name' cannot be null")
        return value


class AccountRead(AccountBase):
    id: int


class TransactionBase(MySQLModel):
    trans_date: date
    amount: Decimal = MoneyField
    vendor: str = StringField
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

    account_id: int | None = Field(
        default=None, foreign_key="account.id", ondelete="SET NULL"
    )
    account: Account | None = Relationship(
        back_populates="transactions",
        sa_relationship_kwargs={
            "lazy": "selectin",
        },
    )


class TransactionCreate(TransactionBase):
    category_id: int | None = None


class TransactionUpdate(TransactionBase):
    trans_date: datetime | None = None
    amount: Decimal | None = OptionalMoneyField
    vendor: str | None = OptionalStringField

    category_id: int | None = None


class TransactionRead(TransactionBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None
    category: CategoryReadNested | None = None


class TransactionPage(PageBase):
    data: list[TransactionRead]


class DeleteResponse(BaseModel):
    detail: str


class MonthlySummary(BaseModel):
    category_id: int | None
    category_name: str | None
    amount_spent: Decimal = MoneyField
    budget: Decimal | None = OptionalMoneyField
