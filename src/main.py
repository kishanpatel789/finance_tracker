from fastapi import FastAPI

from .routers import categories

app = FastAPI()

app.include_router(categories.router)


@app.get("/")
def root():
    return {"message": "Finance Tracker is alive!"}
