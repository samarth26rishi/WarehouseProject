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

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python database.py       # creates events.db from data/events.json
```

## The contract

`docs/event_schema.md` is the source of truth for event fields. Don't change
it without agreeing with the whole team — everyone builds against it.

`docs/api_contract.md` lists the functions Person B exposes and the
endpoints Person C wraps them in.
