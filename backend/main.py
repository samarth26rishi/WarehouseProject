"""
FastAPI application.

Person B owns backend business logic and API endpoints.

Person C consumes these endpoints from the frontend.

No SQL or risk logic should be implemented directly here.
"""

from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from queries import (
    get_events,
    get_event,
    get_summary,
    get_statistics,
    get_highest_risk_events,
)

from assistant import answer_question


app = FastAPI(
    title="Warehouse AI Intelligence API",
    description=(
        "Backend API for AI-powered warehouse handling "
        "risk intelligence."
    ),
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def root():
    return {
        "service": "Warehouse AI Intelligence API",
        "status": "running",
        "docs": "/docs"
    }


# ---------------------------------------------------------
# REQUEST MODEL
# ---------------------------------------------------------

class QuestionRequest(BaseModel):

    question: str


# ---------------------------------------------------------
# HEALTH
# ---------------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "ok",
        "service": "warehouse-ai-backend",
    }


# ---------------------------------------------------------
# EVENTS
# ---------------------------------------------------------

@app.get("/events")
def list_events(
    risk_level: Optional[str] = None,
    behaviour: Optional[str] = None,
    bay: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    limit: Optional[int] = None,
):

    return get_events(
        risk_level=risk_level,
        behaviour=behaviour,
        bay=bay,
        start=start,
        end=end,
        limit=limit,
    )


# ---------------------------------------------------------
# HIGHEST RISK
# ---------------------------------------------------------
# NOTE: this must be declared before the "/events/{event_id}"
# route below — FastAPI matches routes in declaration order,
# and a parameterized path like "/events/{event_id}" would
# otherwise swallow "/events/highest-risk" (matching it as
# event_id="highest-risk") and return 404s.

@app.get("/events/highest-risk")
def highest_risk_events(
    limit: int = 5
):

    return get_highest_risk_events(
        limit=limit
    )


# ---------------------------------------------------------
# SINGLE EVENT
# ---------------------------------------------------------

@app.get("/events/{event_id}")
def get_single_event(
    event_id: str
):

    event = get_event(event_id)

    if not event:

        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    return event


# ---------------------------------------------------------
# SHIFT SUMMARY
# ---------------------------------------------------------

@app.get("/summary/shift")
def summary():

    return get_summary()


# ---------------------------------------------------------
# STATISTICS
# ---------------------------------------------------------

@app.get("/stats")
def stats():

    return get_statistics()


# ---------------------------------------------------------
# AI ASSISTANT
# ---------------------------------------------------------

@app.post("/assistant/query")
def assistant_query(
    request: QuestionRequest
):

    if not request.question.strip():

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    answer = answer_question(
        request.question
    )

    return {
        "question": request.question,
        "answer": answer,
    }