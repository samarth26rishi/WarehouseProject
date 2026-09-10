# B ↔ C Data Contract

Person B exposes these Python functions (in `backend/`). Person C wraps each
in a FastAPI route in `backend/main.py` and calls it from the frontend.
Person C should not reimplement any logic inside these — only call them.

| Function | Module | Wrapped as |
|---|---|---|
| `get_events(risk_level=None, behaviour=None, bay=None, start=None, end=None)` | `queries.py` | `GET /events` |
| `get_event(event_id)` | `queries.py` | `GET /events/{id}` |
| `calculate_risk(event: dict) -> dict` | `risk_engine.py` | used internally by ingest / `get_summary` |
| `get_summary(shift=None)` | `queries.py` | `GET /summary/shift` |
| `get_statistics()` | `queries.py` | `GET /stats` |
| `answer_question(question: str) -> str` | `assistant.py` | `POST /assistant/query` |

## Return shapes

`get_events(...)` → `list[dict]`, each dict matching the stored event schema
(see `event_schema.md`) plus `risk_score`.

`get_summary(shift=None)` → 
```json
{
  "total_events": 42,
  "high_risk_count": 7,
  "critical_count": 2,
  "top_behaviours": [["dragging", 12], ["dropped", 9]],
  "by_bay": {"bay1": 20, "bay2": 22}
}
```

`answer_question(question)` → plain string answer, always grounded in
retrieved events, never claiming confirmed damage — only potential risk.

## Rule
If Person C needs a new way to slice the data (e.g. "top 3 riskiest bays"),
that's a new function in `queries.py` (Person B), not new SQL in `main.py`.
