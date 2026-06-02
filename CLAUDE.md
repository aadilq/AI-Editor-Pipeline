# Mini AI Editor Pipeline

## Project Goal

An end-to-end async clip extraction pipeline that ingests a YouTube video URL, identifies the most engaging moments using AI, and returns short-form clips with rich metadata. Designed for trailers and movie/TV scenes (2–5 min source videos), extracting the top 3 highlights at 15–40 seconds each for maximum viewer retention.

---

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI |
| Async worker | Celery |
| Message broker | Redis |
| Database | PostgreSQL (via SQLAlchemy) |
| Transcription | AssemblyAI (speaker diarization + timestamped segments) |
| LLM scoring | Anthropic Claude API |
| Video download | yt-dlp |
| Clip extraction | FFmpeg (via ffmpeg-python) |
| Containerization | Docker Compose |
| Clip storage | Local bind mount (`./clips/`) |

---

## Architecture

```
Client
  │
  ▼
FastAPI
  ├── POST /submit          → validates URL, creates job, pushes to Redis, returns job_id
  ├── GET  /status/{job_id} → returns job state + clip metadata from PostgreSQL
  └── GET  /clips/{clip_id} → serves clip file via FileResponse
  │
  ▼
Redis (message broker)
  │
  ▼
Celery Worker (sequential pipeline)
  ├── Step 1: Download   — yt-dlp downloads YouTube video to ./clips/
  ├── Step 2: Transcribe — AssemblyAI returns timestamped segments + Speaker A/B labels
  ├── Step 3: Score      — Claude scores each segment (highlight potential, energy, topic)
  └── Step 4: Extract    — FFmpeg cuts top 3 segments, trims to 15–40s, saves to ./clips/
  │
  ▼
PostgreSQL
  ├── jobs table     — job state, video URL, timestamps
  └── clips table    — clip metadata per job (topic, speaker, energy_level, score, file path)
```

---

## Data Flow

1. Client sends `POST /submit` with a YouTube URL
2. API creates a job record (`pending`) in PostgreSQL, enqueues task in Redis, returns `job_id`
3. Celery worker picks up the task and advances the job through states:
   ```
   pending → downloading → transcribing → scoring → extracting → done
   ```
4. AssemblyAI returns segments shaped like:
   ```json
   { "text": "...", "start": 12400, "end": 28700, "speaker": "A" }
   ```
5. Claude receives all segments and returns scores + metadata:
   ```json
   { "segment_index": 2, "score": 0.91, "topic": "climax reveal", "energy_level": "high" }
   ```
6. FFmpeg extracts top 3 scored segments, each clipped to 15–40s
7. Clip file paths + metadata written to PostgreSQL
8. Job state set to `done`; client can `GET /status/{job_id}` to retrieve results

---

## Per-Clip Metadata Schema

```
clip_id       UUID
job_id        FK → jobs
file_path     string (relative path inside ./clips/)
start_time    float (seconds)
end_time      float (seconds)
duration      float (seconds)
score         float (0.0 – 1.0, Claude highlight score)
topic         string (Claude-generated label)
speaker       string ("Speaker A" | "Speaker B" | "Multiple")
energy_level  string ("low" | "medium" | "high")
created_at    timestamp
```

---

## Job State Machine

```
pending → downloading → transcribing → scoring → extracting → done
                                                              ↑
                                                           failed (any step)
```

---

## Build Roadmap

### Phase 1 — Project Scaffold
- [✅] **1.1** Initialize directory structure (`app/`, `worker/`, `db/`, `clips/`)
- [✅] **1.2** Write `requirements.txt` with all dependencies
- [✅] **1.3** Write `docker-compose.yml` with FastAPI, Celery worker, Redis, PostgreSQL services
- [✅] **1.4** Configure bind mount (`./clips:/app/clips`) in Compose

### Phase 2 — Database Layer
- [✅] **2.1** Define SQLAlchemy models: `Job`, `Clip`
- [✅] **2.2** Write Alembic migration (or use `create_all` for dev simplicity)
- [✅] **2.3** Write DB session/engine setup with PostgreSQL connection string from env

### Phase 3 — API Layer
- [✅] **3.1** FastAPI app skeleton with lifespan and DB dependency injection
- [✅] **3.2** `POST /submit` — validate URL, insert job, enqueue Celery task, return `job_id`
- [✅] **3.3** `GET /status/{job_id}` — return job state + associated clips from DB
- [✅] **3.4** `GET /clips/{clip_id}` — serve clip file via `FileResponse`

### Phase 4 — Celery Worker Setup
- [✅] **4.1** Configure Celery app with Redis broker and result backend
- [✅] **4.2** Wire up task to update job state in PostgreSQL at each step
- [✅] **4.3** Implement error handling — catch exceptions, set job state to `failed`

### Phase 5 — Download Step
- [✅] **5.1** Integrate `yt-dlp` to download video from YouTube URL
- [✅] **5.2** Save raw video to `./clips/{job_id}/source.mp4`
- [✅] **5.3** Update job state to `downloading` → `transcribing` on completion

### Phase 6 — Transcription Step
- [✅] **6.1** Integrate AssemblyAI SDK (`aai.Transcriber`)
- [✅] **6.2** Enable speaker diarization and timestamped utterances
- [✅] **6.3** Parse response into a list of segments with `text`, `start`, `end`, `speaker`
- [✅] **6.4** Update job state to `scoring` on completion

### Phase 7 — LLM Scoring Step
- [✅] **7.1** Build Claude prompt that receives all segments and returns scored JSON
- [✅] **7.2** Parse Claude response into ranked segment list with `score`, `topic`, `energy_level`
- [✅] **7.3** Select top 3 segments; enforce 15–40s clip window around each
- [ ] **7.4** Update job state to `extracting` on completion

### Phase 8 — Clip Extraction Step
- [ ] **8.1** Integrate `ffmpeg-python` to cut clips from source video at exact timestamps
- [ ] **8.2** Output clips to `./clips/{job_id}/clip_1.mp4`, `clip_2.mp4`, `clip_3.mp4`
- [ ] **8.3** Write clip records to PostgreSQL with full metadata
- [ ] **8.4** Update job state to `done` on completion

### Phase 9 — Integration & Polish
- [ ] **9.1** End-to-end smoke test with a real YouTube trailer URL
- [ ] **9.2** Verify clip files accessible via filesystem (`./clips/`) and `GET /clips/{clip_id}`
- [ ] **9.3** Tune Claude prompt based on scoring quality
- [ ] **9.4** Add basic input validation (URL format, YouTube domain check)
