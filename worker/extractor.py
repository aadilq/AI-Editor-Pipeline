import ffmpeg
from db.models import Clip
from worker.uploader import upload_public_file
import os
from dotenv import load_dotenv

load_dotenv()


def extract_clips(job_id: int, top_clips: list[dict], source_path: str, db) -> None:

    for i, clip in enumerate(top_clips):
        input_file = source_path
        output_file = f"/app/clips/{job_id}/clip_{i+1}.mp4"


        ffmpeg.input(input_file, ss=clip["start_second"], to=clip["end_second"]).output(output_file, af="volume=1.5", vcodec="copy", acodec="aac").run()
        gcs_url = upload_public_file(bucket_name=os.getenv("GCS_BUCKET_NAME"), source_file_path=output_file, destination_blob_name=f"{job_id}/clip_{i+1}.mp4")
        final_clip = Clip(
            job_id=job_id,
            file_path=gcs_url,
            start_time=clip["start_second"],
            end_time=clip["end_second"],
            duration=clip["duration"],
            score=clip["score"],
            topic=clip["topic"],
            speaker=clip["speaker"],
            energy_level=clip["energy_level"]
        )
        db.add(final_clip)
        db.commit()
        
        
                
        