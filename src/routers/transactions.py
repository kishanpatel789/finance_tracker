from fastapi import APIRouter, HTTPException

from ..dependencies import SessionDep
from ..models import (
    Category,
    Transaction,
    TransactionCreate,
    TransactionRead,
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
