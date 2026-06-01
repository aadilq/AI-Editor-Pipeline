import assemblyai as aai
import os
from dotenv import load_dotenv

load_dotenv()


aai.settings.base_url = "https://api.assemblyai.com"
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

def transcribe_video(source_path: str) -> list[dict]:
    config = aai.TranscriptionConfig(speaker_labels=True)
    transcriber = aai.Transcriber(config=config)
    transcript = transcriber.transcribe(source_path)

    
    return [{"text": utterance.text, "start": utterance.start, "end": utterance.end, "speaker": utterance.speaker}
            for utterance in transcript.utterances]
    
