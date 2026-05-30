from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from db.session import get_db
from sqlalchemy.orm import Session
from db.models import Job
from pydantic import BaseModel, HttpUrl


class SubmitPayload(BaseModel):
    url: HttpUrl


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
def submit(payload: SubmitPayload, db: Session = Depends(get_db), ):
    video_url = str(payload.url)
    job = Job(status="pending", video_url=video_url)
    db.add(job)
    db.commit()
    db.refresh(job)
    return {"job_id": job.id}
    


