# Warehouse AI Project — GEG Hackathon

AI video intelligence for warehouse handling: detect risky handling behaviour,
score risk, and let an AI assistant explain/query it.

## Ownership

| Folder | Owner | Purpose |
|---|---|---|
| `perception/` | Person A | Video → detection/tracking → `events.json` |
| `backend/` | Person B | SQLite, risk engine, RAG-lite AI assistant |
| `frontend/` | Person C | Dashboard, video overlays, chat UI |
| `docs/` | Shared | Event schema, API contract, deck |

## Setup

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python database.py       # creates events.db from data/events.json
uvicorn main:app --reload --port 8000
```

The `/assistant/query` endpoint calls a local **Ollama** model (`qwen2.5:3b`),
not the `anthropic` package listed in `requirements.txt` — install
[Ollama](https://ollama.com) and run `ollama pull qwen2.5:3b` if you want the
chat assistant tab to work. Everything else (events, stats, dashboard) only
needs the FastAPI server above.

### Frontend

```bash
cd frontend
npm install               # or bun install
cp .env.example .env      # VITE_API_URL — defaults to http://localhost:8000
npm run dev                # or bun dev
```

## The contract

`docs/event_schema.md` is the source of truth for event fields. Don't change
it without agreeing with the whole team — everyone builds against it.

`docs/api_contract.md` lists the functions Person B exposes and the
endpoints Person C wraps them in.
