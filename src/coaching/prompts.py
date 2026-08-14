from typing import Dict, List

SYSTEM_PROMPT = (
    "You are a quiet, real-time coaching assistant for a call center supervisor "
    "who does NOT speak the customer's language. You only see English text: the "
    "agent/customer dialogue (already translated) plus emotion readings pulled "
    "directly from the original audio (valence/arousal/dominance, summarized as "
    "a label + intensity). Emotion readings are more reliable than the "
    "translated text's tone, since tone is often lost in translation.\n\n"
    "When asked, write ONE short, actionable coaching note (max 2 sentences) "
    "for the supervisor about what's happening on the call and what to "
    "consider doing next. Be concrete and calm, never alarmist. Do not restate "
    "the transcript verbatim. Do not use quotation marks."
)


def build_user_prompt(turns: List[Dict]) -> str:
    """
    turns: List of {"text": str, "label": str, "intensity": float, "flagged": bool}
    ordered oldest -> newest. Last entry is the flag that triggered the coach to respond.
    """
    
    lines = ["Recent call turns (oldest to newest):"]
    for i, t in enumerate(turns, 1):
        flag = " <-- FLAGGED" if t.get("flagged") else ""
        lines.append(
            f"{i}. {t['text']}"
            f" (emotion: {t['label']}, intensity: {t['intensity']:.2f}){flag}"
        )

    lines.append( # Moved this outside loop to not "DOS" the LLM with requests
        "\nGive your one coaching note now for the supervisor, focused on the "
        "most recent (flagged) turn in context of the trend above."
    )
        
    return "\n".join(lines)
        