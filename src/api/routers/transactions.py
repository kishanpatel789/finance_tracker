import re
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import or_, select

from ..dependencies import SessionDep
from ..helpers import create_page
from ..models import (
    Category,
    DeleteResponse,
    PaginationInput,
    Transaction,
    TransactionCreate,
    TransactionPage,
    TransactionQueryParams,
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
    request: Request,
    session: SessionDep,
    pagination_input: Annotated[PaginationInput, Depends()],
    query_params: Annotated[TransactionQueryParams, Depends()],
):
    query_map: dict = query_params.model_dump()

    # search filter
    query = select(Transaction)
    if query_params.q is not None:
        q = query_params.q.strip().lower()
        q = re.sub(r"\s+", " ", q)
        query_map.update({"q": q})
        search_term = f"%{q}%"
        query = query.where(
            or_(
                Transaction.vendor.ilike(
                    search_term
                ),  # ty: ignore[unresolved-attribute]
                Transaction.note.ilike(search_term),  # ty: ignore[unresolved-attribute]
                Transaction.category.has(
                    Category.name.ilike(search_term)
                ),  # ty: ignore[unresolved-attribute]
            )
        )

    # date range filter
    if query_params.start_date is not None:
        query = query.where(Transaction.trans_date >= query_params.start_date)
    if query_params.end_date is not None:
        query = query.where(Transaction.trans_date <= query_params.end_date)

    # sort
    query = query.order_by(
        Transaction.trans_date.desc(),  # ty: ignore[unresolved-attribute]
        Transaction.vendor.desc(),  # ty: ignore[unresolved-attribute]
        Transaction.amount.desc(),  # ty: ignore[unresolved-attribute]
    )

    page_output = create_page(query, query_map, pagination_input, session, request)

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
