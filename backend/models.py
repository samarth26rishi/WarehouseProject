"""
Event data model.

This is the in-memory / SQL-row representation of an event, derived from the
shared schema in docs/event_schema.md. Person A's raw events.json feeds the
first set of fields; the rest are filled in by Person B on ingest.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Event:
    event_id: str
    timestamp_video: str
    camera_id: str
    behaviour: str
    confidence: float

    # Derived by Person B on ingest
    bay: Optional[str] = None
    risk_level: Optional[str] = None          # Low / Medium / High / Critical
    risk_score: Optional[int] = None
    explanation: Optional[str] = None

    # Raw extras from Person A, kept as JSON strings in SQLite
    objects: list = field(default_factory=list)
    evidence: dict = field(default_factory=dict)

    def derive_bay(self):
        """camera_id like 'bay1_cam1' -> 'bay1'."""
        if self.camera_id and "_" in self.camera_id:
            self.bay = self.camera_id.split("_")[0]
        else:
            self.bay = self.camera_id
        return self.bay

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_raw(raw: dict) -> "Event":
        """Build an Event from a raw record out of events.json."""
        ev = Event(
            event_id=raw["event_id"],
            timestamp_video=raw["timestamp_video"],
            camera_id=raw["camera_id"],
            behaviour=raw["behaviour"],
            confidence=raw.get("confidence", 0.0),
            objects=raw.get("objects", []),
            evidence=raw.get("evidence", {}),
        )
        ev.derive_bay()
        return ev


# SQLite table definition — keep in sync with the fields above
CREATE_EVENTS_TABLE = """
CREATE TABLE IF NOT EXISTS events (
    event_id        TEXT PRIMARY KEY,
    timestamp_video TEXT NOT NULL,
    camera_id       TEXT NOT NULL,
    bay             TEXT,
    behaviour       TEXT NOT NULL,
    confidence      REAL,
    risk_level      TEXT,
    risk_score      INTEGER,
    explanation     TEXT,
    objects_json    TEXT,
    evidence_json   TEXT
);
"""
