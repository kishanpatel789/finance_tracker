from fastapi import FastAPI

from .routers import categories, transactions

app = FastAPI()

app.include_router(categories.router)
app.include_router(transactions.router)


@app.get("/")
def root():
    return {"message": "Finance Tracker is alive!"}
