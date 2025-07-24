import re
from datetime import date, datetime, timezone
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import func, or_, select

from ..dependencies import PaginationDep, SessionDep
from ..models import (
    Category,
    DeleteResponse,
    Transaction,
    TransactionCreate,
    TransactionPage,
    TransactionRead,
    TransactionUpdate,
)

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
)


@router.post("/", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(transaction: TransactionCreate, session: SessionDep):
    db_transaction = Transaction.model_validate(
        transaction.model_dump(exclude={"category_id"})
    )
    if transaction.category_id is not None:
        category = session.get(Category, transaction.category_id)
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        db_transaction.category = category

    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction


@router.get("/", response_model=TransactionPage)
def read_transactions(
    session: SessionDep,
    pagination_input: PaginationDep,
    q: Annotated[str | None, Query(max_length=40)] = None,
    start_date: date | None = None,
    end_date: date | None = None,
):
    query = select(Transaction)

    # search filter
    if q is not None:
        q = q.strip().lower()
        q = re.sub(r"\s+", " ", q)
        search_term = f"%{q}%"
        query = query.where(
            or_(
                Transaction.vendor.ilike(search_term),
                Transaction.note.ilike(search_term),
                Transaction.category.has(Category.name.ilike(search_term)),
            )
        )

    # date range filter
    if start_date is not None:
        query = query.where(Transaction.trans_date >= start_date)

    if end_date is not None:
        query = query.where(Transaction.trans_date <= end_date)

    # get total record count
    count_query = select(func.count(1).label("cnt")).select_from(query.subquery())
    total_row_count = session.exec(count_query).one()

    # calculate total page count
    total_page_count = (
        total_row_count + pagination_input.size - 1
    ) // pagination_input.size

    # determine actual page to give; give last page if requested page is out of bounds
    page = min(
        pagination_input.page,
        max(total_page_count, 1),  # give at least page 1 if no records
    )

    # pagination
    offset = (page - 1) * pagination_input.size
    query = (
        query.order_by(
            Transaction.trans_date.desc(),
            Transaction.vendor.desc(),
            Transaction.amount.desc(),
        )
        .offset(offset)
        .limit(pagination_input.size)
    )
    transactions = session.exec(query).all()

    page_output = TransactionPage(
        data=transactions,
        total_count=total_row_count,
    )

    return page_output


@router.get("/{transaction_id}", response_model=TransactionRead)
def read_transaction(transaction_id: int, session: SessionDep):
    transaction = session.get(Transaction, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.patch("/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    transaction_id: int, transaction: TransactionUpdate, session: SessionDep
):
    db_transaction = session.get(Transaction, transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    transaction_data = transaction.model_dump(exclude_unset=True)
    for key, value in transaction_data.items():
        setattr(db_transaction, key, value)

    if (
        "category_id" in transaction_data
        and transaction_data["category_id"] is not None
    ):
        category = session.get(Category, transaction_data["category_id"])
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        db_transaction.category = category

    db_transaction.updated_at = datetime.now(timezone.utc)

    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction


@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: int, session: SessionDep) -> DeleteResponse:
    db_transaction = session.get(Transaction, transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    session.delete(db_transaction)
    session.commit()
    return DeleteResponse(
        detail=f"Transaction with ID {transaction_id} deleted successfully"
    )
