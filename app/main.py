from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from db.session import get_db
from sqlalchemy.orm import Session
from db.models import Job, Clip
from pydantic import BaseModel, HttpUrl

from fastapi.responses import FileResponse


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
def submit(payload: SubmitPayload, db: Session = Depends(get_db)):
    video_url = str(payload.url)
    job = Job(status="pending", video_url=video_url)
    db.add(job)
    db.commit()
    db.refresh(job)
    # TODO: enqueue celery task
    # sends the task to the message broker (Redis)
    # process_video.delay(job.id)
    return {"job_id": job.id}
    


@app.get("/status/{job_id}")
def get_job_status(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_status": job.status, "job_clips": []}

@app.get("/clips/{clip_id}")
def serve_clip(clip_id: int, db: Session = Depends(get_db)):
    clip = db.query(Clip).filter(Clip.clip_id == clip_id).first()
    if clip is None:
        raise HTTPException(status_code=404, detail="Clip not found")
    return FileResponse(clip.file_path, media_type="video/mp4")