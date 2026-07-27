# Setting the neutral point and margin for mapping scores
NEUTRAL_VALENCE = 0.4
NEUTRAL_AROUSAL = 0.4
NEUTRAL_DOMINANCE = 0.4
MARGIN = 0.05


def _bucket(value: float, neutral: float, margin: float) -> str:
    """Bucket the value into 'low', 'neutral' or 'high' based on the neutral value and margin."""
    if value < neutral - margin:
        return "low"
    elif value > neutral + margin:
        return "high"
    else:
        return "neutral"


def describe(valence: float, arousal: float, dominance: float) -> dict:
    """
    Describe the emotion based on the valence, arousal and dominance scores.
    This is a heuristic that maps the scores to a readable description of the emotion.
    """
    v = _bucket(valence, NEUTRAL_VALENCE, MARGIN)
    a = _bucket(arousal, NEUTRAL_AROUSAL, MARGIN)
    d = _bucket(dominance, NEUTRAL_DOMINANCE, MARGIN)

    # distance from the neutral point
    # Right now we only use this for flagging
    # but it can be very useful for more detailed emotion capture
    # We can use this to add an extra dimension to the LLM input for better context
    intensity = (
        (valence - NEUTRAL_VALENCE) ** 2
        + (arousal - NEUTRAL_AROUSAL) ** 2
        + (dominance - NEUTRAL_DOMINANCE) ** 2
    ) ** 0.5

    # --- Octant mapping ---
    # +V+A+D = Exuberant/Excited      -V+A+D = Hostile/Angry
    # +V-A+D = Relaxed/Content        -V-A+D = Disdainful/Contemptuous
    # +V+A-D = Dependent/Eager        -V+A-D = Anxious/Distressed
    # +V-A-D = Docile/Calm            -V-A-D = Bored/Disengaged
    if v == "high" and a == "high" and d == "high":
        label = "Excited / Enthusiastic"
    elif v == "low" and a == "high" and d == "high":
        label = "Angry / Hostile"
    elif v == "high" and a == "low" and d == "high":
        label = "Relaxed / Content"
    elif v == "low" and a == "low" and d == "high":
        label = "Disdainful / Contemptuous"
    elif v == "high" and a == "high" and d == "low":
        label = "Eager / Enthusiastic (submissive)"
    elif v == "low" and a == "high" and d == "low":
        label = "Distressed / Anxious"
    elif v == "high" and a == "low" and d == "low":
        label = "Calm / Docile"
    elif v == "low" and a == "low" and d == "low":
        label = "Disengaged / Bored"
    else:
        # Any dimension still in the deadzone -> not confident enough
        # to call a full octant, fall back to a 2-axis read.
        if v == "low" and a == "high":
            label = "Negative / Agitated"
        elif v == "low":
            label = "Negative"
        elif a == "high":
            label = "High energy"
        else:
            label = "Calm / Neutral"

    # Flag for escalation: anything low-valence with meaningful
    # intensity, regardless of dominance (covers both "angry" and "distressed").
    flagged = v == "low" and intensity > MARGIN

    return {
        "label": label,
        "intensity": round(intensity, 3),
        "flagged": flagged,
    }
