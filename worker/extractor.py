import ffmpeg


def extract_clips(job_id: int, top_clips: list[dict], source_path: str, db) -> None:

    for i, clip in enumerate(top_clips):
        input_file = source_path
        output_file = f"/app/clips/{job_id}/clip_{i+1}.mp4"
        
                
        