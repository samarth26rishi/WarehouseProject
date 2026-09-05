"""
LLM-powered assistant, grounded only in the real event log (RAG-lite).

Flow: question -> retrieve relevant events from SQLite -> build context ->
send to LLM with a guardrail system prompt -> return grounded answer.

No vector DB, no embeddings — keyword/filter matching against SQLite events
is "retrieval" enough for this scope.
"""

import os
import re

from anthropic import Anthropic
from queries import get_events, get_summary

client = Anthropic()  # reads ANTHROPIC_API_KEY from environment
MODEL = "claude-sonnet-4-6"

GUARDRAIL_SYSTEM_PROMPT = """You are a warehouse safety assistant. You answer \
questions ONLY using the event data provided in the context below. Rules:

1. Never claim a product was confirmed damaged. Only describe observed \
behaviour and potential/estimated risk (e.g. "this represents a potential \
product-damage risk"), unless the event data explicitly states confirmed damage.
2. Never invent events, counts, or numbers that are not in the provided context.
3. If the context doesn't contain enough information to answer, say so plainly \
instead of guessing.
4. Keep answers concise and factual, suitable for a warehouse supervisor.
"""

# Very simple keyword -> filter mapping. Extend as real questions come in.
BEHAVIOUR_KEYWORDS = {
    "drop": "product_dropped",
    "drag": "dragging",
    "stack": "unstable_stacking",
    "step": "stepping_on_product",
}
RISK_KEYWORDS = {"high": "High", "critical": "Critical", "medium": "Medium", "low": "Low"}


def retrieve_relevant_events(question: str, limit: int = 15) -> list[dict]:
    """
    Naive keyword-based retrieval: pull filters out of the question text,
    then query SQLite. Falls back to the most recent events if nothing
    matches, so the assistant always has *something* grounded to work from.
    """
    q = question.lower()

    behaviour = next((v for k, v in BEHAVIOUR_KEYWORDS.items() if k in q), None)
    risk_level = next((v for k, v in RISK_KEYWORDS.items() if k in q), None)
    bay = None
    match = re.search(r"bay\s*(\d+)", q)
    if match:
        bay = f"bay{match.group(1)}"

    events = get_events(risk_level=risk_level, behaviour=behaviour, bay=bay)
    return events[-limit:] if events else get_events()[-limit:]


def build_context(events: list[dict]) -> str:
    if not events:
        return "No matching events found in the event log."

    lines = []
    for e in events:
        lines.append(
            f"- {e['event_id']} @ {e['timestamp_video']} ({e['bay']}): "
            f"{e['behaviour']} — risk: {e['risk_level']} (score {e['risk_score']}). "
            f"{e['explanation']}"
        )
    return "\n".join(lines)


def answer_question(question: str) -> str:
    events = retrieve_relevant_events(question)
    context = build_context(events)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        # Fallback so the pipeline is testable before an API key is wired up
        return (
            "[LLM not configured — set ANTHROPIC_API_KEY] "
            f"Retrieved {len(events)} relevant events. Raw context:\n{context}"
        )

    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        system=GUARDRAIL_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Event log context:\n{context}\n\nQuestion: {question}",
            }
        ],
    )
    return "".join(block.text for block in response.content if block.type == "text")


if __name__ == "__main__":
    print(answer_question("What were the high risk events at bay1?"))
