from fastapi import FastAPI

from .routers import categories, transactions

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
    version="0.0.1",
    contact={
        "name": "Kishan Patel",
        "url": "https://kishanpatel.dev",
        "email": "kishanpatel789@gmail.com",
    },
    openapi_tags=tags_metadata,
)

app.include_router(categories.router)
app.include_router(transactions.router)


@app.get("/")
def root():
    return {"message": "Finance Tracker is alive!"}
