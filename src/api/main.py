from fastapi import FastAPI

from .helpers import parse_pyproject_toml
from .routers import categories, reports, transactions

project_info = parse_pyproject_toml()

description = """
This API supports the Finance Tracker application frontend.
Data for the application can be manipulated directly through this API.

## Categories 🗃️

You can **create**, **read**, **update**, and **delete** categories. Categories are used to classify transactions.

## Transactions 💸

You can **create**, **read**, **update**, and **delete** transactions.

## Reports 📈

You can **generate** reports to analyze your financial data. Reports can be filtered by date range and category.

[ IN PROGRESS ]
"""

tags_metadata = [
    {
        "name": "categories",
        "description": "Manage categories.",
    },
    {
        "name": "transactions",
        "description": "Manage transactions.",
    },
]

app = FastAPI(
    title="Finance Tracker 💰",
    description=description,
    summary="Record transactions and audit your finances against a monthly budget.",
    version=project_info.version,
    contact={
        "name": project_info.author_name,
        "url": "https://kishanpatel.dev",
        "email": project_info.author_email,
    },
    openapi_tags=tags_metadata,
)

app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(reports.router)


@app.get("/")
def root():
    return {"message": "Finance Tracker is alive!"}
