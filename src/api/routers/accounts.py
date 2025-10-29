from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from ..dependencies import SessionDep
from ..models import (
    Account,
    AccountCreate,
    AccountRead,
    AccountUpdate,
    DeleteResponse,
)

router = APIRouter(
    prefix="/accounts",
    tags=["accounts"],
)


def _check_for_existing_account(session: SessionDep, account_name: str) -> None:
    """Check if a account with the given name already exists."""

    db_account_existing = session.exec(
        select(Account).where(Account.name == account_name)
    ).first()
    if db_account_existing is not None:
        raise HTTPException(
            status_code=409,
            detail=f"Account with name '{account_name}' already exists (ID {db_account_existing.id})",
        )


def _account_name_changed(account_data: dict, db_account: Account) -> bool:
    return "name" in account_data and account_data["name"] != db_account.name


@router.post("/", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
def create_account(account: AccountCreate, session: SessionDep):
    db_account = Account.model_validate(account)

    _check_for_existing_account(session, account.name)

    session.add(db_account)
    session.commit()
    session.refresh(db_account)
    return db_account


@router.get("/", response_model=list[AccountRead])
def read_accounts(session: SessionDep):
    accounts = session.exec(select(Account).order_by(Account.name)).all()
    return accounts


@router.get("/{account_id}", response_model=AccountRead)
def read_account(account_id: int, session: SessionDep):
    account = session.get(Account, account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.patch("/{account_id}", response_model=AccountRead)
def update_account(account_id: int, account: AccountUpdate, session: SessionDep):
    db_account = session.get(Account, account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    account_data = account.model_dump(exclude_unset=True)
    if _account_name_changed(account_data, db_account):
        _check_for_existing_account(session, account_data["name"])
    for key, value in account_data.items():
        setattr(db_account, key, value)

    session.add(db_account)
    session.commit()
    session.refresh(db_account)
    return db_account


@router.delete("/{account_id}")
def delete_account(account_id: int, session: SessionDep) -> DeleteResponse:
    db_account = session.get(Account, account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    session.delete(db_account)
    session.commit()
    return DeleteResponse(detail=f"Account with ID {account_id} deleted successfully")
