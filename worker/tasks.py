from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_URL = f"redis://:{REDIS_PASSWORD}@redis:6379/0"

app = Celery(
    'task_workers',
    broker=REDIS_URL,
    backend=REDIS_URL
)

