# Logging project's stats/metrics

import csv
import os
import uuid
from datetime import datetime

LOG_PATH = "src/evaluation/evaluation_log.csv"

COLUMNS = [
    "utterance_id",
    "session_id",
    "timestamp",
    "language",
    "original_text",
    "translated_text",
    "arousal",
    "valence",
    "dominance",
    "label",
    "intensity",
    "flagged",
    "coaching_note",
    "latency_ms",
]


def _ensure_header():
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            writer.writeheader()


def generate_utterance_id() -> str:
    return str(uuid.uuid4())


def log_utterance(
    utterance_id: str,
    session_id: str,
    language: str,
    original_text: str,
    translated_text: str,
    arousal: float,
    valence: float,
    dominance: float,
    label: str,
    intensity: float,
    flagged: bool,
):
    _ensure_header()
    row = {
        "utterance_id": utterance_id,
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "language": language,
        "original_text": original_text,
        "translated_text": translated_text,
        "arousal": round(arousal, 3),
        "valence": round(valence, 3),
        "dominance": round(dominance, 3),
        "label": label,
        "intensity": round(intensity, 3),
        "flagged": flagged,
        "coaching_note": "",
        "latency_ms": "",
    }
    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writerow(row)


def log_coaching(utterance_id: str, note: str, latency_ms: float):
    if not os.path.exists(LOG_PATH):
        return

    rows = []
    with open(LOG_PATH, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["utterance_id"] == utterance_id:
                row["coaching_note"] = note
                row["latency_ms"] = round(latency_ms, 2)
            rows.append(row)

    with open(LOG_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)