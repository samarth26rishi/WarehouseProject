"""
Rule-based risk scoring engine.

Deterministic, explainable, no ML. Converts an Event into a risk_score,
risk_level, and a plain-language explanation that never claims confirmed
damage — only potential risk (the responsible-AI guardrail).
"""

from models import Event

# Base points per behaviour type
BEHAVIOUR_SCORES = {
    "product_dropped": 40,
    "dragging": 20,
    "unstable_stacking": 30,
    "stepping_on_product": 35,
    "rough_handling": 25,
    "wrong_equipment": 15,
    "outside_designated_area": 10,
}

REPEATED_EVENT_BONUS = 20          # same behaviour + bay seen recently
LOW_CONFIDENCE_PENALTY = -10       # confidence < 0.6 -> less certain -> lower score
HIGH_CONFIDENCE_BONUS = 5          # confidence > 0.9

# Score -> category thresholds
THRESHOLDS = [
    (70, "Critical"),
    (45, "High"),
    (20, "Medium"),
    (0, "Low"),
]


def score_to_level(score: int) -> str:
    for threshold, level in THRESHOLDS:
        if score >= threshold:
            return level
    return "Low"


def calculate_risk(event: Event, recent_same_behaviour_count: int = 0) -> dict:
    """
    Returns {"risk_score": int, "risk_level": str, "explanation": str,
    "triggered_rules": list[str]}.

    recent_same_behaviour_count: how many times this behaviour has already
    occurred at this bay in the current shift (pass 0 if not tracking yet —
    queries.py can compute this and pass it in later).
    """
    triggered = []
    score = 0

    base = BEHAVIOUR_SCORES.get(event.behaviour, 15)
    score += base
    triggered.append(f"behaviour '{event.behaviour}' base risk +{base}")

    if event.confidence is not None:
        if event.confidence >= 0.9:
            score += HIGH_CONFIDENCE_BONUS
            triggered.append(f"high detection confidence ({event.confidence:.2f}) +{HIGH_CONFIDENCE_BONUS}")
        elif event.confidence < 0.6:
            score += LOW_CONFIDENCE_PENALTY
            triggered.append(f"low detection confidence ({event.confidence:.2f}) {LOW_CONFIDENCE_PENALTY}")

    if recent_same_behaviour_count > 0:
        score += REPEATED_EVENT_BONUS
        triggered.append(
            f"repeated '{event.behaviour}' at {event.bay} "
            f"({recent_same_behaviour_count}x this shift) +{REPEATED_EVENT_BONUS}"
        )

    score = max(0, score)
    level = score_to_level(score)

    explanation = (
        f"Observed: {event.behaviour.replace('_', ' ')} at {event.bay or event.camera_id} "
        f"(confidence {event.confidence:.2f}). "
        f"Rules triggered: {'; '.join(triggered)}. "
        f"Resulting score {score} -> {level} risk. "
        f"This represents a potential product-damage risk, not confirmed damage."
    )

    return {
        "risk_score": score,
        "risk_level": level,
        "explanation": explanation,
        "triggered_rules": triggered,
    }
