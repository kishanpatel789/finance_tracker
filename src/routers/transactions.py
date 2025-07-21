from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from ..dependencies import SessionDep
from ..models import (
    Category,
    DeleteResponse,
    Transaction,
    TransactionCreate,
    TransactionRead,
    TransactionUpdate,
)

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
)


@router.post("/", response_model=TransactionRead)
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


@router.get("/", response_model=list[TransactionRead])
def read_transactions(session: SessionDep):
    transactions = session.exec(select(Transaction)).all()
    return transactions


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
