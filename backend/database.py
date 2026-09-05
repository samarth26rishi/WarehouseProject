"""
SQLite connection and event storage.

Owns: schema creation, importing events.json into SQLite, inserting/updating
individual event rows. This is the only module that talks to the database
file directly — queries.py reads through here, nothing else should.
"""

import json
import sqlite3
from pathlib import Path

from models import Event, CREATE_EVENTS_TABLE
from risk_engine import calculate_risk

DB_PATH = Path(__file__).parent / "data" / "events.db"
EVENTS_JSON_PATH = Path(__file__).parent / "data" / "events.json"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(CREATE_EVENTS_TABLE)
    conn.commit()
    conn.close()


def insert_event(conn: sqlite3.Connection, event: Event):
    conn.execute(
        """
        INSERT OR REPLACE INTO events
        (event_id, timestamp_video, camera_id, bay, behaviour, confidence,
         risk_level, risk_score, explanation, objects_json, evidence_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event.event_id,
            event.timestamp_video,
            event.camera_id,
            event.bay,
            event.behaviour,
            event.confidence,
            event.risk_level,
            event.risk_score,
            event.explanation,
            json.dumps(event.objects),
            json.dumps(event.evidence),
        ),
    )


def import_events_from_json(path: Path = EVENTS_JSON_PATH):
    """
    Load raw events (from Person A's pipeline, or the mock file), run each
    through the risk engine, and store the result in SQLite.
    """
    with open(path) as f:
        raw_events = json.load(f)

    conn = get_connection()
    count = 0
    for raw in raw_events:
        event = Event.from_raw(raw)
        risk = calculate_risk(event)
        event.risk_level = risk["risk_level"]
        event.risk_score = risk["risk_score"]
        event.explanation = risk["explanation"]
        insert_event(conn, event)
        count += 1

    conn.commit()
    conn.close()
    return count


if __name__ == "__main__":
    init_db()
    n = import_events_from_json()
    print(f"Imported {n} events into {DB_PATH}")
