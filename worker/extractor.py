import ffmpeg
from db.models import Clip


def extract_clips(job_id: int, top_clips: list[dict], source_path: str, db) -> None:

    for i, clip in enumerate(top_clips):
        input_file = source_path
        output_file = f"/app/clips/{job_id}/clip_{i+1}.mp4"


        ffmpeg.input(input_file, ss=clip["start_second"], to=clip["end_second"]).output(output_file, af="volume-1.5", vcodec="copy", acodec="aac").run()
        final_clip = Clip(
            job_id=job_id,
            file_path=output_file,
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
        
        
                
        