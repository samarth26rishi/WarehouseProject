"""
Deterministic warehouse risk scoring engine.

This module does NOT use ML.

It converts observed behaviour into:
    - risk_score
    - risk_level
    - explanation
    - triggered_rules

The engine describes potential risk, not confirmed product damage.
"""

from models import Event


# ---------------------------------------------------------
# BASE RISK BY OBSERVED BEHAVIOUR
# ---------------------------------------------------------

BEHAVIOUR_SCORES = {
    "product_thrown": 45,
    "product_dropped": 40,
    "stepping_on_product": 35,
    "unstable_stacking": 30,
    "product_rolling": 25,
    "rough_handling": 25,
    "dragging": 20,
    "wrong_equipment": 15,
    "outside_designated_area": 10,
}


# ---------------------------------------------------------
# MODIFIERS
# ---------------------------------------------------------

REPEATED_EVENT_BONUS = 20

LOW_CONFIDENCE_PENALTY = -10

HIGH_CONFIDENCE_BONUS = 5


# ---------------------------------------------------------
# RISK THRESHOLDS
# ---------------------------------------------------------

THRESHOLDS = [
    (70, "Critical"),
    (45, "High"),
    (20, "Medium"),
    (0, "Low"),
]


def score_to_level(score: int) -> str:
    """
    Convert numerical risk score into a risk category.
    """

    for threshold, level in THRESHOLDS:
        if score >= threshold:
            return level

    return "Low"


def calculate_risk(
    event: Event,
    recent_same_behaviour_count: int = 0
) -> dict:
    """
    Calculate risk for a single event.

    recent_same_behaviour_count:
        Number of previous occurrences of the same behaviour
        at the same bay during the current event stream.

    Returns:
        {
            "risk_score": int,
            "risk_level": str,
            "explanation": str,
            "triggered_rules": list
        }
    """

    triggered_rules = []

    # -----------------------------------------------------
    # 1. BASE BEHAVIOUR SCORE
    # -----------------------------------------------------

    base_score = BEHAVIOUR_SCORES.get(
        event.behaviour,
        15
    )

    score = base_score

    triggered_rules.append(
        f"Behaviour '{event.behaviour}' "
        f"base risk +{base_score}"
    )

    # -----------------------------------------------------
    # 2. CONFIDENCE MODIFIER
    # -----------------------------------------------------

    confidence = event.confidence

    if confidence >= 0.90:

        score += HIGH_CONFIDENCE_BONUS

        triggered_rules.append(
            f"High detection confidence "
            f"({confidence:.2f}) "
            f"+{HIGH_CONFIDENCE_BONUS}"
        )

    elif confidence < 0.60:

        score += LOW_CONFIDENCE_PENALTY

        triggered_rules.append(
            f"Low detection confidence "
            f"({confidence:.2f}) "
            f"{LOW_CONFIDENCE_PENALTY}"
        )

    # -----------------------------------------------------
    # 3. REPEATED BEHAVIOUR
    # -----------------------------------------------------

    if recent_same_behaviour_count > 0:

        score += REPEATED_EVENT_BONUS

        triggered_rules.append(
            f"Repeated behaviour at {event.bay} "
            f"({recent_same_behaviour_count} "
            f"previous occurrence(s)) "
            f"+{REPEATED_EVENT_BONUS}"
        )

    # -----------------------------------------------------
    # 4. SAFETY
    # -----------------------------------------------------

    score = max(0, score)

    # -----------------------------------------------------
    # 5. RISK LEVEL
    # -----------------------------------------------------

    risk_level = score_to_level(score)

    # -----------------------------------------------------
    # 6. EXPLANATION
    # -----------------------------------------------------

    explanation = (
        f"Observed {event.behaviour.replace('_', ' ')} "
        f"at {event.bay} using {event.camera_id}. "
        f"Detection confidence was {confidence:.2f}. "
        f"{' '.join(triggered_rules)} "
        f"Final risk score: {score}, classified as "
        f"{risk_level} risk. "
        f"This indicates potential handling or "
        f"product-safety risk and does not confirm "
        f"product damage."
    )

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "explanation": explanation,
        "triggered_rules": triggered_rules,
    }