import os
import anthropic
import json

from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

def score_segments(segments: list[dict]) -> list[dict]:

    custom_system_prompt = """
    You are going to be given a list of segments as JSON. the keys of the json response are explained as below.
    The segment's text is going to be "text", the segment's start time is "start", the segment's end time is
    "end" and segment's speaker is going to be "speaker". With each segment, you are to score it based on the
    excitement and energy level. Look at word choices, phrases, punctuation, etc that show some level of excitement. Return only valid
    json - no explanation text, just the array. for each segment of the array, return the segment_index(specific time-chunk), score(0.0 - 1.0), topic,
    and energy_level(low/medium/high). 
    """
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=10000,
            system=custom_system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": json.dumps(segments)
                }
            ]
        )
        raw = response.content[0].text.strip()
        print(f"RAW CLAUDE RESPONSE: {repr(raw)}")
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
            raw = raw.rstrip("```").strip()
        scored = json.loads(raw)
        for item in scored:
            original = segments[item["segment_index"]]
            item["start"] = original["start"]
            item["end"] = original["end"]
            item["speaker"] = original["speaker"]
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored
        
    except Exception as e:
        raise RuntimeError(f"An error has occurred: {str(e)}")