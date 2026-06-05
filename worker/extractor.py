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


        duration = clip["end_second"] - clip["start_second"]
        stream = ffmpeg.input(input_file, ss=clip["start_second"])
        video = stream.video
        audio = stream.audio.filter("volume", 1.5)
        ffmpeg.output(video, audio, output_file, vcodec="libx264", acodec="aac", t=duration).run(overwrite_output=True)
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
        
        
                
        