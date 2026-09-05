"""
SQL retrieval and aggregation logic.

These are the functions Person C's FastAPI routes call directly. Do not put
SQL anywhere else in the project (not in main.py, not in the frontend).
"""

import json
from database import get_connection


def _row_to_dict(row) -> dict:
    d = dict(row)
    d["objects"] = json.loads(d.pop("objects_json") or "[]")
    d["evidence"] = json.loads(d.pop("evidence_json") or "{}")
    return d


def get_events(risk_level=None, behaviour=None, bay=None, start=None, end=None) -> list[dict]:
    """
    Filtered event list. All filters optional. `start`/`end` filter on
    timestamp_video (string comparison works for HH:MM:SS format).
    """
    conn = get_connection()
    query = "SELECT * FROM events WHERE 1=1"
    params = []

    if risk_level:
        query += " AND risk_level = ?"
        params.append(risk_level)
    if behaviour:
        query += " AND behaviour = ?"
        params.append(behaviour)
    if bay:
        query += " AND bay = ?"
        params.append(bay)
    if start:
        query += " AND timestamp_video >= ?"
        params.append(start)
    if end:
        query += " AND timestamp_video <= ?"
        params.append(end)

    query += " ORDER BY timestamp_video ASC"

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_event(event_id: str) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM events WHERE event_id = ?", (event_id,)).fetchone()
    conn.close()
    return _row_to_dict(row) if row else None


def get_statistics() -> dict:
    """Grouped counts for dashboard charts."""
    conn = get_connection()

    by_risk = conn.execute(
        "SELECT risk_level, COUNT(*) as count FROM events GROUP BY risk_level"
    ).fetchall()
    by_bay = conn.execute(
        "SELECT bay, COUNT(*) as count FROM events GROUP BY bay"
    ).fetchall()
    by_behaviour = conn.execute(
        "SELECT behaviour, risk_level, COUNT(*) as count FROM events GROUP BY behaviour, risk_level"
    ).fetchall()

    conn.close()
    return {
        "by_risk_level": {r["risk_level"]: r["count"] for r in by_risk},
        "by_bay": {r["bay"]: r["count"] for r in by_bay},
        "by_behaviour_and_risk": [dict(r) for r in by_behaviour],
    }


def get_summary(shift: str | None = None) -> dict:
    """
    Structured, dashboard-ready shift summary. `shift` is currently unused
    (single-pilot scope has no shift boundaries yet) — wire it in once
    Person A's events carry real timestamps to bucket by.
    """
    conn = get_connection()

    total = conn.execute("SELECT COUNT(*) as c FROM events").fetchone()["c"]
    high_risk = conn.execute(
        "SELECT COUNT(*) as c FROM events WHERE risk_level = 'High'"
    ).fetchone()["c"]
    critical = conn.execute(
        "SELECT COUNT(*) as c FROM events WHERE risk_level = 'Critical'"
    ).fetchone()["c"]
    top_behaviours = conn.execute(
        "SELECT behaviour, COUNT(*) as c FROM events GROUP BY behaviour ORDER BY c DESC LIMIT 3"
    ).fetchall()
    by_bay = conn.execute(
        "SELECT bay, COUNT(*) as c FROM events GROUP BY bay"
    ).fetchall()

    conn.close()
    return {
        "total_events": total,
        "high_risk_count": high_risk,
        "critical_count": critical,
        "top_behaviours": [[r["behaviour"], r["c"]] for r in top_behaviours],
        "by_bay": {r["bay"]: r["c"] for r in by_bay},
    }
