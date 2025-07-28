import tomllib
from pathlib import Path

from fastapi import FastAPI

from .routers import categories, transactions

project_root = Path(__file__).parents[2]
with open(project_root / "pyproject.toml", "rb") as f:
    pyproject = tomllib.load(f)

VERSION = pyproject["project"]["version"]
AUTHOR_NAME = pyproject["project"]["authors"][0]["name"]
AUTHOR_EMAIL = pyproject["project"]["authors"][0]["email"]


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
    version=VERSION,
    contact={
        "name": AUTHOR_NAME,
        "url": "https://kishanpatel.dev",
        "email": AUTHOR_EMAIL,
    },
    openapi_tags=tags_metadata,
)

app.include_router(categories.router)
app.include_router(transactions.router)


@app.get("/")
def root():
    return {"message": "Finance Tracker is alive!"}
