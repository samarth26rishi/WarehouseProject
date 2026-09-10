# Event Schema (locked Day 1 — do not change without team agreement)

Source: master project doc, section 3.2.

```json
{
  "event_id": "evt_00123",
  "timestamp_video": "00:02:14",
  "camera_id": "bay1_cam1",
  "objects": ["person_2", "box_7"],
  "behaviour": "product_dropped",
  "confidence": 0.87,
  "risk_level": "High",
  "evidence": {
    "clip_start": "00:02:11",
    "clip_end": "00:02:17",
    "frame_snapshot": "frame_00123.jpg"
  },
  "explanation": "Box carried by person_2 lost contact with hands and fell ~1m before impact."
}
```

## Fields Person A produces (in `events.json`)
- `event_id`, `timestamp_video`, `camera_id`, `objects`, `behaviour`, `confidence`, `evidence`

## Fields Person B derives and stores (in SQLite, added on ingest)
- `bay` (parsed from `camera_id`, e.g. `bay1_cam1` → `bay1`)
- `risk_level` (Low / Medium / High / Critical)
- `risk_score` (numeric, from `risk_engine.py`)
- `explanation` (Person B's grounded explanation, may differ from A's raw note)

Person A may still fill a rough `risk_level` for their own testing — Person B's
risk engine is the one that overwrites it once events reach SQLite.
