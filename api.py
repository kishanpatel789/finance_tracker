from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Finance Tracker is alive!"}
