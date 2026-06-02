import os
import anthropic
import json

from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

def score_segments(segments: list[dict]) -> list[dict]:

    custom_system_prompt = """
    You are an expert video editor specializing in short-form content for trailers and movie/TV scenes.
    You will be given a list of transcript segments as JSON with keys: "text", "start", "end", "speaker".

    Your job is to score each segment on its potential to make a viewer feel something — goosebumps, suspense,
    shock, emotional investment, or the urge to keep watching. Prioritize segments that contain:
    - Dramatic reveals or plot twists
    - Emotional confrontations or vulnerable moments
    - High-stakes dialogue ("we only have one shot", "I can't let you do this")
    - Tension-building exchanges between characters
    - Powerful one-liners or memorable quotes
    - Moments of triumph, sacrifice, or loss

    Deprioritize segments that are purely expository, transitional, or low-stakes small talk.

    Return only valid JSON — no explanation text, just the array.
    For each segment return: segment_index, score (0.0-1.0), topic (short descriptive label), energy_level (low/medium/high).
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