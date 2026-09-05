"""
FastAPI application — owned by Person C.

This is a minimal starter so Person C can run something on Day 1; Person C
should build this out. Wraps Person B's functions from queries.py and
assistant.py — no business logic should be added here directly.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from queries import get_events, get_event, get_summary, get_statistics
from assistant import answer_question

app = FastAPI(title="Warehouse AI API")


class QuestionRequest(BaseModel):
    question: str


@app.get("/events")
def list_events(risk_level: str = None, behaviour: str = None, bay: str = None):
    return get_events(risk_level=risk_level, behaviour=behaviour, bay=bay)


@app.get("/events/{event_id}")
def get_single_event(event_id: str):
    event = get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@app.get("/summary/shift")
def summary():
    return get_summary()


@app.get("/stats")
def stats():
    return get_statistics()


@app.post("/assistant/query")
def assistant_query(req: QuestionRequest):
    return {"answer": answer_question(req.question)}
