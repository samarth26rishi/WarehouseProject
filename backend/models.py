"""
Data models for warehouse events.

Person A produces the raw perception fields.
Person B enriches them with bay, risk score, risk level and explanation.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Event:
    # Fields produced by Person A
    event_id: str
    timestamp_video: str
    camera_id: str
    behaviour: str
    confidence: float

    # Raw perception information
    objects: list = field(default_factory=list)
    evidence: dict = field(default_factory=dict)

    # Fields derived by Person B
    bay: Optional[str] = None
    risk_level: Optional[str] = None
    risk_score: Optional[int] = None
    explanation: Optional[str] = None

    def derive_bay(self) -> str:
        """
        Convert camera ID into a bay.

        Example:
            bay1_cam1 -> bay1
            bay2_cam1 -> bay2
        """
        if not self.camera_id:
            self.bay = "unknown"
            return self.bay

        parts = self.camera_id.split("_")

        if parts:
            self.bay = parts[0]
        else:
            self.bay = self.camera_id

        return self.bay

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_raw(raw: dict) -> "Event":
        """
        Convert one raw Person A event into an Event object.
        """

        required_fields = [
            "event_id",
            "timestamp_video",
            "camera_id",
            "behaviour",
            "confidence",
        ]

        missing = [
            field for field in required_fields
            if field not in raw
        ]

        if missing:
            raise ValueError(
                f"Event is missing required fields: {missing}"
            )

        event = Event(
            event_id=raw["event_id"],
            timestamp_video=raw["timestamp_video"],
            camera_id=raw["camera_id"],
            behaviour=raw["behaviour"],
            confidence=float(raw.get("confidence", 0.0)),
            objects=raw.get("objects", []),
            evidence=raw.get("evidence", {}),
        )

        event.derive_bay()

        return event


CREATE_EVENTS_TABLE = """
CREATE TABLE IF NOT EXISTS events (
    event_id        TEXT PRIMARY KEY,
    timestamp_video TEXT NOT NULL,
    camera_id       TEXT NOT NULL,
    bay             TEXT NOT NULL,
    behaviour       TEXT NOT NULL,
    confidence      REAL NOT NULL,

    risk_level      TEXT NOT NULL,
    risk_score      INTEGER NOT NULL,
    explanation     TEXT NOT NULL,

    objects_json    TEXT,
    evidence_json   TEXT
);
"""