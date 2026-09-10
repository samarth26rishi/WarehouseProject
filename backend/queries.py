"""
Database retrieval and aggregation functions.

The API and assistant should call these functions instead of
writing SQL themselves.
"""

import json

from database import get_connection


# ---------------------------------------------------------
# ROW -> DICTIONARY
# ---------------------------------------------------------

def _row_to_dict(row) -> dict:

    if row is None:
        return None

    data = dict(row)

    data["objects"] = json.loads(
        data.pop("objects_json") or "[]"
    )

    data["evidence"] = json.loads(
        data.pop("evidence_json") or "{}"
    )

    return data


# ---------------------------------------------------------
# GET EVENTS
# ---------------------------------------------------------

def get_events(
    risk_level=None,
    behaviour=None,
    bay=None,
    start=None,
    end=None,
    limit=None
) -> list[dict]:

    conn = get_connection()

    query = """
        SELECT *
        FROM events
        WHERE 1=1
    """

    params = []

    if risk_level:

        query += """
            AND risk_level = ?
        """

        params.append(risk_level)

    if behaviour:

        query += """
            AND behaviour = ?
        """

        params.append(behaviour)

    if bay:

        query += """
            AND bay = ?
        """

        params.append(bay)

    if start:

        query += """
            AND timestamp_video >= ?
        """

        params.append(start)

    if end:

        query += """
            AND timestamp_video <= ?
        """

        params.append(end)

    query += """
        ORDER BY timestamp_video ASC
    """

    if limit is not None:

        query += """
            LIMIT ?
        """

        params.append(limit)

    rows = conn.execute(
        query,
        params
    ).fetchall()

    conn.close()

    return [
        _row_to_dict(row)
        for row in rows
    ]


# ---------------------------------------------------------
# GET SINGLE EVENT
# ---------------------------------------------------------

def get_event(event_id: str):

    conn = get_connection()

    row = conn.execute(
        """
        SELECT *
        FROM events
        WHERE event_id = ?
        """,
        (event_id,)
    ).fetchone()

    conn.close()

    return _row_to_dict(row) if row else None


# ---------------------------------------------------------
# STATISTICS
# ---------------------------------------------------------

def get_statistics() -> dict:

    conn = get_connection()

    total = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM events
        """
    ).fetchone()["count"]

    by_risk = conn.execute(
        """
        SELECT
            risk_level,
            COUNT(*) AS count
        FROM events
        GROUP BY risk_level
        """
    ).fetchall()

    by_bay = conn.execute(
        """
        SELECT
            bay,
            COUNT(*) AS count
        FROM events
        GROUP BY bay
        """
    ).fetchall()

    by_behaviour = conn.execute(
        """
        SELECT
            behaviour,
            COUNT(*) AS count
        FROM events
        GROUP BY behaviour
        ORDER BY count DESC
        """
    ).fetchall()

    behaviour_risk = conn.execute(
        """
        SELECT
            behaviour,
            risk_level,
            COUNT(*) AS count
        FROM events
        GROUP BY behaviour, risk_level
        ORDER BY behaviour, risk_level
        """
    ).fetchall()

    conn.close()

    return {
        "total_events": total,

        "by_risk_level": {
            row["risk_level"]: row["count"]
            for row in by_risk
        },

        "by_bay": {
            row["bay"]: row["count"]
            for row in by_bay
        },

        "by_behaviour": {
            row["behaviour"]: row["count"]
            for row in by_behaviour
        },

        "by_behaviour_and_risk": [
            dict(row)
            for row in behaviour_risk
        ],
    }


# ---------------------------------------------------------
# SHIFT SUMMARY
# ---------------------------------------------------------

def get_summary(
    shift: str | None = None
) -> dict:

    conn = get_connection()

    total = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM events
        """
    ).fetchone()["count"]

    high = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM events
        WHERE risk_level = 'High'
        """
    ).fetchone()["count"]

    critical = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM events
        WHERE risk_level = 'Critical'
        """
    ).fetchone()["count"]

    medium = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM events
        WHERE risk_level = 'Medium'
        """
    ).fetchone()["count"]

    low = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM events
        WHERE risk_level = 'Low'
        """
    ).fetchone()["count"]

    top_behaviours = conn.execute(
        """
        SELECT
            behaviour,
            COUNT(*) AS count
        FROM events
        GROUP BY behaviour
        ORDER BY count DESC
        LIMIT 3
        """
    ).fetchall()

    by_bay = conn.execute(
        """
        SELECT
            bay,
            COUNT(*) AS count
        FROM events
        GROUP BY bay
        """
    ).fetchall()

    risk_by_bay = conn.execute(
        """
        SELECT
            bay,
            COUNT(*) AS high_risk_events
        FROM events
        WHERE risk_level IN ('High', 'Critical')
        GROUP BY bay
        ORDER BY high_risk_events DESC
        """
    ).fetchall()

    conn.close()

    return {
        "total_events": total,

        "risk_distribution": {
            "Critical": critical,
            "High": high,
            "Medium": medium,
            "Low": low,
        },

        "high_risk_count": high,

        "critical_count": critical,

        "top_behaviours": [
            [row["behaviour"], row["count"]]
            for row in top_behaviours
        ],

        "by_bay": {
            row["bay"]: row["count"]
            for row in by_bay
        },

        "high_risk_by_bay": {
            row["bay"]: row["high_risk_events"]
            for row in risk_by_bay
        },
    }


# ---------------------------------------------------------
# HIGHEST RISK EVENTS
# ---------------------------------------------------------

def get_highest_risk_events(
    limit: int = 5
) -> list[dict]:

    conn = get_connection()

    rows = conn.execute(
        """
        SELECT *
        FROM events
        ORDER BY risk_score DESC,
                 timestamp_video ASC
        LIMIT ?
        """,
        (limit,)
    ).fetchall()

    conn.close()

    return [
        _row_to_dict(row)
        for row in rows
    ]