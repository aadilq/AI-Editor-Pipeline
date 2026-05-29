from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from db.session import get_db
from sqlalchemy.orm import Session


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application is starting up...")
    yield
    print("Application is shutting down...")


app = FastAPI(lifespan=lifespan)
@app.get("/")
def read_index():
    return {"message": "Hello, FastAPI!"}

@app.post("/submit")
def submit(db: Session = Depends(get_db)):
    return


