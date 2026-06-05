import yt_dlp
import os

def download_video(job_id: int, video_url: str) -> str:
    output_dir = f"/app/clips/{job_id}"
    os.makedirs(output_dir, exist_ok=True)

    # Configure the options
    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": f"{output_dir}/source.mp4",
        "merge_output_format": "mp4",
    }

    # Execute the download context
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
    return f"{output_dir}/source.mp4"
    