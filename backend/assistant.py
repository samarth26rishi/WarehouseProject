"""
Warehouse AI - Qwen2.5 RAG-lite Assistant

Responsibilities:
    - Accept natural-language warehouse questions
    - Retrieve relevant information from SQLite
    - Answer factual questions directly from the database
    - Use Qwen2.5:3b for explanations and summaries
    - Keep answers concise and grounded in warehouse data
"""

import json
import re
import sqlite3
from pathlib import Path

import ollama


# =========================================================
# CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "data" / "events.db"

MODEL = "qwen2.5:3b"

# Keep generation short for faster responses.
NUM_PREDICT = 100

# Low temperature = more factual / less creative.
TEMPERATURE = 0.1


# =========================================================
# DATABASE
# =========================================================

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# =========================================================
# DATABASE HELPERS
# =========================================================

def get_total_events(conn):
    row = conn.execute(
        "SELECT COUNT(*) AS count FROM events"
    ).fetchone()

    return row["count"]


def get_behaviour_counts(conn):
    rows = conn.execute(
        """
        SELECT behaviour, COUNT(*) AS count
        FROM events
        GROUP BY behaviour
        ORDER BY count DESC
        """
    ).fetchall()

    return {
        row["behaviour"]: row["count"]
        for row in rows
    }


def get_risk_counts(conn):
    rows = conn.execute(
        """
        SELECT risk_level, COUNT(*) AS count
        FROM events
        GROUP BY risk_level
        ORDER BY count DESC
        """
    ).fetchall()

    return {
        row["risk_level"]: row["count"]
        for row in rows
    }


def get_events_by_behaviour(conn, behaviour):
    rows = conn.execute(
        """
        SELECT
            event_id,
            timestamp_video,
            camera_id,
            bay,
            behaviour,
            confidence,
            risk_level,
            risk_score
        FROM events
        WHERE behaviour = ?
        ORDER BY timestamp_video, event_id
        """,
        (behaviour,)
    ).fetchall()

    return [dict(row) for row in rows]


def get_events_by_bay(conn, bay):
    rows = conn.execute(
        """
        SELECT
            event_id,
            timestamp_video,
            camera_id,
            bay,
            behaviour,
            confidence,
            risk_level,
            risk_score
        FROM events
        WHERE LOWER(bay) = LOWER(?)
        ORDER BY timestamp_video, event_id
        """,
        (bay,)
    ).fetchall()

    return [dict(row) for row in rows]


def get_all_events(conn):
    rows = conn.execute(
        """
        SELECT
            event_id,
            timestamp_video,
            camera_id,
            bay,
            behaviour,
            confidence,
            risk_level,
            risk_score
        FROM events
        ORDER BY timestamp_video, event_id
        """
    ).fetchall()

    return [dict(row) for row in rows]


# =========================================================
# DATA SUMMARIZATION
# =========================================================

def build_warehouse_summary(conn):
    total = get_total_events(conn)
    behaviours = get_behaviour_counts(conn)
    risks = get_risk_counts(conn)

    all_events = get_all_events(conn)

    if all_events:
        first_timestamp = all_events[0]["timestamp_video"]
        last_timestamp = all_events[-1]["timestamp_video"]
    else:
        first_timestamp = "unknown"
        last_timestamp = "unknown"

    bays = sorted(
        {
            event["bay"]
            for event in all_events
            if event["bay"]
        }
    )

    return {
        "total_events": total,
        "behaviours": behaviours,
        "risk_levels": risks,
        "bays": bays,
        "time_range": {
            "start": first_timestamp,
            "end": last_timestamp
        }
    }


# =========================================================
# WAREHOUSE TERMINOLOGY
# =========================================================

WAREHOUSE_TERMINOLOGY = """
Warehouse terminology:
- product_thrown = a product was physically thrown in the warehouse.
- product_dropped = a product was observed being dropped.
- product_rolling = a product was observed rolling.
- These are warehouse event labels detected by the perception system.
- "product_thrown" does NOT mean creating, repeating, manufacturing,
  or iterating a product.
"""


# =========================================================
# FORMAT EVENT RESULTS
# =========================================================

def format_event_list(events):
    if not events:
        return "No matching events found."

    lines = []

    for event in events:
        lines.append(
            f"- {event['event_id']} | "
            f"{event['timestamp_video']} | "
            f"{event['bay']} | "
            f"{event['behaviour']} | "
            f"{event['risk_level']} "
            f"({event['risk_score']})"
        )

    return "\n".join(lines)


# =========================================================
# SIMPLE QUESTION DETECTION
# =========================================================

def detect_behaviour(question):
    q = question.lower()

    if (
        "product thrown" in q
        or "product throwing" in q
        or "products thrown" in q
        or "throwing" in q
        or "thrown" in q
    ):
        return "product_thrown"

    if (
        "product dropped" in q
        or "products dropped" in q
        or "dropping" in q
        or "dropped" in q
    ):
        return "product_dropped"

    if (
        "product rolling" in q
        or "products rolling" in q
        or "rolling" in q
        or "rolled" in q
    ):
        return "product_rolling"

    return None


def detect_bay(question):
    match = re.search(
        r"\b(bay\d+)\b",
        question.lower()
    )

    if match:
        return match.group(1)

    return None


# =========================================================
# DIRECT RETRIEVAL QUESTIONS
# =========================================================

def answer_retrieval_question(question, conn):
    q = question.lower().strip()

    behaviour = detect_behaviour(question)

    # -----------------------------------------------------
    # "Which events..."
    # -----------------------------------------------------

    if behaviour and (
        "which events" in q
        or "what events" in q
        or "show me the events" in q
        or "list the events" in q
    ):
        events = get_events_by_behaviour(
            conn,
            behaviour
        )

        if not events:
            return f"No events with behaviour '{behaviour}' were found."

        lines = [
            f"Found {len(events)} matching warehouse events:"
        ]

        lines.extend(
            format_event_list(events).splitlines()
        )

        return "\n".join(lines)

    # -----------------------------------------------------
    # "How many..."
    # -----------------------------------------------------

    if behaviour and (
        "how many" in q
        or "number of" in q
        or "count of" in q
    ):
        events = get_events_by_behaviour(
            conn,
            behaviour
        )

        return (
            f"There were {len(events)} "
            f"'{behaviour}' events."
        )

    # -----------------------------------------------------
    # High risk count
    # -----------------------------------------------------

    if (
        "how many" in q
        and "high risk" in q
    ):
        risks = get_risk_counts(conn)

        return (
            f"There were "
            f"{risks.get('High', 0)} High-risk events."
        )

    # -----------------------------------------------------
    # Events in a bay
    # -----------------------------------------------------

    bay = detect_bay(question)

    if bay and (
        "how many" in q
        and ("events" in q or "incidents" in q)
    ):
        events = get_events_by_bay(
            conn,
            bay
        )

        return (
            f"There were {len(events)} "
            f"recorded events in {bay}."
        )

    # -----------------------------------------------------
    # Return None if Qwen should handle it
    # -----------------------------------------------------

    return None


# =========================================================
# BUILD CONTEXT FOR QWEN
# =========================================================

def build_context(question, conn):
    summary = build_warehouse_summary(conn)

    behaviour = detect_behaviour(question)
    bay = detect_bay(question)

    context = []

    context.append(WAREHOUSE_TERMINOLOGY)

    context.append(
        "Warehouse summary:"
    )

    context.append(
        f"- Total events: {summary['total_events']}"
    )

    context.append(
        f"- Behaviours: "
        f"{json.dumps(summary['behaviours'])}"
    )

    context.append(
        f"- Risk levels: "
        f"{json.dumps(summary['risk_levels'])}"
    )

    context.append(
        f"- Bays: {', '.join(summary['bays'])}"
    )

    context.append(
        f"- Time range: "
        f"{summary['time_range']['start']} "
        f"to "
        f"{summary['time_range']['end']}"
    )

    # -----------------------------------------------------
    # Relevant behaviour information
    # -----------------------------------------------------

    if behaviour:

        events = get_events_by_behaviour(
            conn,
            behaviour
        )

        context.append(
            f"\nRelevant behaviour: {behaviour}"
        )

        context.append(
            f"- Matching events: {len(events)}"
        )

        if events:

            risk_distribution = {}

            for event in events:
                level = event["risk_level"]

                risk_distribution[level] = (
                    risk_distribution.get(level, 0) + 1
                )

            context.append(
                f"- Risk distribution: "
                f"{json.dumps(risk_distribution)}"
            )

            bays = sorted(
                {
                    event["bay"]
                    for event in events
                    if event["bay"]
                }
            )

            context.append(
                f"- Bays involved: "
                f"{', '.join(bays)}"
            )

            context.append(
                f"- First event: "
                f"{events[0]['timestamp_video']}"
            )

            context.append(
                f"- Last event: "
                f"{events[-1]['timestamp_video']}"
            )

    # -----------------------------------------------------
    # Relevant bay information
    # -----------------------------------------------------

    if bay:

        events = get_events_by_bay(
            conn,
            bay
        )

        context.append(
            f"\nRelevant bay: {bay}"
        )

        context.append(
            f"- Events in bay: {len(events)}"
        )

        behaviour_counts = {}

        for event in events:

            behaviour_counts[event["behaviour"]] = (
                behaviour_counts.get(
                    event["behaviour"],
                    0
                ) + 1
            )

        context.append(
            f"- Behaviour distribution: "
            f"{json.dumps(behaviour_counts)}"
        )

        risk_counts = {}

        for event in events:

            risk_counts[event["risk_level"]] = (
                risk_counts.get(
                    event["risk_level"],
                    0
                ) + 1
            )

        context.append(
            f"- Risk distribution: "
            f"{json.dumps(risk_counts)}"
        )

    return "\n".join(context)


# =========================================================
# QWEN RESPONSE
# =========================================================

def ask_qwen(question, context):

    system_prompt = """
You are a concise warehouse safety assistant.

Your job is to answer the supervisor's question using ONLY
the warehouse information supplied in the context.

IMPORTANT RULES:

1. Give ONLY the final answer.
2. Do not show reasoning or analysis.
3. Do not say "We are given", "Let's analyze", "First",
   "Hmm", or similar meta-commentary.
4. Do not discuss product development, manufacturing,
   product iterations, or regulatory compliance unless
   explicitly present in the warehouse context.
5. In this system, "product_thrown" means a physical product
   was thrown in the warehouse.
6. Never invent workers, causes, intentions, injuries,
   damage, costs, or other facts.
7. If the data does not establish something, say that the
   available data does not establish it.
8. Keep the answer concise: normally 1-3 sentences.
9. Use concrete numbers from the supplied data when useful.
"""

    user_prompt = f"""
{context}

Supervisor question:
{question}

Answer directly and concisely.
"""

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt.strip()
            },
            {
                "role": "user",
                "content": user_prompt.strip()
            }
        ],
        options={
            "temperature": TEMPERATURE,
            "num_predict": NUM_PREDICT
        }
    )

    answer = response["message"]["content"].strip()

    return clean_qwen_response(answer)


# =========================================================
# CLEAN QWEN OUTPUT
# =========================================================

def clean_qwen_response(answer):

    # Remove accidental markdown fences.
    answer = answer.replace("```text", "")
    answer = answer.replace("```", "")

    # Remove Qwen's occasional meta opening.
    bad_openings = [
        "We are given the warehouse facts and the question:",
        "We are given the warehouse data and the question:",
        "We are given the warehouse facts:",
        "Let's tackle this question.",
        "Let's analyze this.",
        "Okay, let's tackle this question.",
        "First, let's understand the question.",
    ]

    for opening in bad_openings:

        if answer.lower().startswith(
            opening.lower()
        ):
            answer = answer[
                len(opening):
            ].strip()

    # Remove leading "Answer:".
    if answer.lower().startswith("answer:"):
        answer = answer[7:].strip()

    return answer


# =========================================================
# MAIN QUESTION HANDLER
# =========================================================

def answer_question(question):

    conn = get_connection()

    try:

        # -------------------------------------------------
        # First: try deterministic database retrieval.
        # This is much faster than calling Qwen.
        # -------------------------------------------------

        direct_answer = answer_retrieval_question(
            question,
            conn
        )

        if direct_answer is not None:
            return direct_answer

        # -------------------------------------------------
        # Otherwise: build compact RAG context.
        # -------------------------------------------------

        context = build_context(
            question,
            conn
        )

    finally:
        conn.close()

    # -----------------------------------------------------
    # Ask Qwen for explanation/synthesis.
    # -----------------------------------------------------

    return ask_qwen(
        question,
        context
    )


# =========================================================
# COMMAND LINE INTERFACE
# =========================================================

def main():

    print("==============================================")
    print("Warehouse AI - Qwen2.5 RAG-lite Assistant")
    print("==============================================")
    print(f"Model: {MODEL}")
    print("Qwen thinking: N/A (Qwen2.5)")
    print("Type 'exit' to stop.")
    print()

    while True:

        try:
            question = input("You: ").strip()

        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

        if not question:
            continue

        if question.lower() in {
            "exit",
            "quit"
        }:
            print("Exiting...")
            break

        print()

        try:

            answer = answer_question(
                question
            )

            print(
                f"Assistant: {answer}"
            )

        except Exception as e:

            print(
                "\nAssistant error:"
            )

            print(e)

        print()


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()