from typing import Annotated

from fastapi import APIRouter, Query
from sqlmodel import case, func, nulls_last, outerjoin, select

from ..dependencies import SessionDep
from ..helpers import get_month_range
from ..models import (
    Category,
    MonthlySummary,
    Transaction,
)

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
)


@router.get("/monthly_budget", response_model=list[MonthlySummary])
def get_monthly_report(
    year_month: Annotated[str, Query(pattern=r"\d{4}-\d{2}")], session: SessionDep
):
    start_date, end_date = get_month_range(year_month)

    # subquery to aggregate transactions
    subq = (
        select(
            Transaction.category_id, func.sum(Transaction.amount).label("amount_spent")
        )
        .where(
            Transaction.trans_date >= start_date,
            Transaction.trans_date <= end_date,
        )
        .group_by(Transaction.category_id)
        .subquery()
    )

    # final query to get category info
    query = (
        select(
            Category.id.label("category_id"),
            Category.name.label("category_name"),
            func.coalesce(subq.c.amount_spent, 0).label("amount_spent"),
            Category.budget,
        )
        .select_from(
            outerjoin(Category, subq, Category.id == subq.c.category_id, full=True)
        )
        .order_by(
            case((Category.budget.is_(None), 1), else_=0), nulls_last(Category.name)
        )
    )

    data = session.exec(query).all()

    return data
