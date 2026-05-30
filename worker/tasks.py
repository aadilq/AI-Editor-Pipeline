from celery import Celery
import os
from dotenv import load_dotenv
from db.models import Job
from db.session import SessionLocal

load_dotenv()

REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_URL = f"redis://:{REDIS_PASSWORD}@redis:6379/0"

app = Celery(
    'task_workers',
    broker=REDIS_URL,
    backend=REDIS_URL
)

@app.task
def process_video(job_id: int):
    db = SessionLocal()
    try:
        current_job = db.query(Job).filter(Job.id == job_id).first()

        ## Step 1: Downloading
        current_job.status = "downloading"
        db.commit()
        # ... downloading logic ...

        ## Step 2: Transcribing
        current_job.status = "transcribing"
        db.commit()
        # ... transcribing logic ...

        ## Step 3: LLM Scoring
        current_job.status = "scoring"
        db.commit()
        # ... scoring logic ...

        ## Step 4: Extracting
        current_job.status = "extracting"
        db.commit()
        # ... extracting logic ...

        current_job.status = "done"
        db.commit()
    except Exception as e:
        current_job = db.query(Job).filter(Job.id == job_id).first()
        current_job.status = "failed"
        current_job.error_message = str(e)
        db.commit()
    finally:
        db.close()
