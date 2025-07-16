from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship




class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    budget: float

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
        sa_relationship_kwargs={
            "lazy": "selectin",
        },
)
