from celery import Celery
import os
from dotenv import load_dotenv
from db.models import Job
from db.session import SessionLocal
from worker.downloader import download_video
from worker.transcriber import transcribe_video
from worker.scorer import score_segments

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
        source_path = download_video(job_id, current_job.video_url)
        # ... downloading logic ...

        ## Step 2: Transcribing
        current_job.status = "transcribing"
        db.commit()
        segments = transcribe_video(source_path=source_path)

        # ... transcribing logic ...

        ## Step 3: LLM Scoring
        current_job.status = "scoring"
        db.commit()
        scored_segments = score_segments(segments)
        top_clips = scored_segments[:3]

        for clip in top_clips:
            start_second = clip["start"] / 1000
            end_second = clip["end"] / 1000
            duration = end_second - start_second

            if duration < 15:
                end_second = start_second + 15
            elif duration > 40:
                end_second = start_second + 40
            clip["start_second"] = start_second
            clip["end_second"] = end_second
            clip["duration"] = end_second - start_second
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
