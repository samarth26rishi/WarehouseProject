"""
Database layer.

Responsibilities:
    - Create SQLite database
    - Create events table
    - Import events.json
    - Calculate derived risk information
    - Store enriched events

Only this module directly manages database writes.
"""

import json
import sqlite3
from pathlib import Path

from models import Event, CREATE_EVENTS_TABLE
from risk_engine import calculate_risk


BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "data" / "events.db"

EVENTS_JSON_PATH = BASE_DIR / "data" / "events.json"


# ---------------------------------------------------------
# CONNECTION
# ---------------------------------------------------------

def get_connection() -> sqlite3.Connection:

    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row

    return conn


# ---------------------------------------------------------
# DATABASE INITIALIZATION
# ---------------------------------------------------------

def init_db():

    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    conn = get_connection()

    conn.execute(CREATE_EVENTS_TABLE)

    conn.commit()

    conn.close()


# ---------------------------------------------------------
# INSERT EVENT
# ---------------------------------------------------------

def insert_event(
    conn: sqlite3.Connection,
    event: Event
):

    conn.execute(
        """
        INSERT OR REPLACE INTO events
        (
            event_id,
            timestamp_video,
            camera_id,
            bay,
            behaviour,
            confidence,
            risk_level,
            risk_score,
            explanation,
            objects_json,
            evidence_json
        )
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
        )
    )


# ---------------------------------------------------------
# IMPORT EVENTS
# ---------------------------------------------------------

def import_events_from_json(
    path: Path = EVENTS_JSON_PATH
):
    """
    Load Person A's events.json.

    For each event:

        raw JSON
             ↓
        Event object
             ↓
        derive bay
             ↓
        calculate risk
             ↓
        store in SQLite
    """

    with open(path, "r", encoding="utf-8") as f:

        raw_events = json.load(f)

    if not isinstance(raw_events, list):

        raise ValueError(
            "events.json must contain a JSON array."
        )

    init_db()

    conn = get_connection()

    # Tracks previous occurrences of:
    #
    # (bay, behaviour)
    #
    # Example:
    # ("bay1", "product_dropped")
    #
    behaviour_history = {}

    imported = 0

    try:

        # Sort by video timestamp
        raw_events = sorted(
            raw_events,
            key=lambda e: e["timestamp_video"]
        )

        for raw in raw_events:

            event = Event.from_raw(raw)

            key = (
                event.bay,
                event.behaviour
            )

            previous_count = behaviour_history.get(
                key,
                0
            )

            # Calculate risk with repetition information
            risk = calculate_risk(
                event,
                recent_same_behaviour_count=previous_count
            )

            event.risk_score = risk["risk_score"]

            event.risk_level = risk["risk_level"]

            event.explanation = risk["explanation"]

            insert_event(
                conn,
                event
            )

            behaviour_history[key] = (
                previous_count + 1
            )

            imported += 1

        conn.commit()

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()

    return imported


# ---------------------------------------------------------
# COMMAND LINE ENTRY
# ---------------------------------------------------------

if __name__ == "__main__":

    count = import_events_from_json()

    print(
        f"Imported {count} events into:"
        f"\n{DB_PATH}"
    )