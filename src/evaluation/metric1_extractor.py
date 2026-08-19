# This only extracts rows which contain coaching feedback so that the evaluation of the first metric can be done
# Metric 1: Tone-Text Agreement (Manual Rubric)

# For every row in the CSV where coaching_note is not empty, read the note and score it on two dimensions:

# Dimension 1 - Tone Alignment (1-3): Does the note reflect the emotion label in the label column?

# 3: clearly references or responds to the hostile/intense tone (mentions escalation, de-escalation, aggression, anger)
# 2: somewhat relevant but vague, could apply to any call
# 1: ignores the tone signal entirely, generic advice unrelated to the emotion

# Dimension 2 - Actionability (1-3): Is the advice concrete and useful for a supervisor?

# 3: specific action suggested (e.g. "escalate to manager", "acknowledge the customer's wait time")
# 2: general direction given but not specific enough to act on immediately
# 1: too vague to act on ("be empathetic", "handle professionally")

# Average both dimensions separately across all scored notes per model. Do this for both Ollama and OpenAI coaching notes. Higher average = better.


import pandas as pd

# Load both labeled logs
ollama = pd.read_csv("src/evaluation/evaluation_log_labeled_ollama.csv")
openai = pd.read_csv("src/evaluation/evaluation_log_labeled_openai.csv")

# Add model column
ollama["model"] = "ollama"
openai["model"] = "openai"

# Pull only rows where coaching note exists
ollama_notes = ollama[ollama["coaching_note"].notna() & (ollama["coaching_note"] != "")]
openai_notes = openai[openai["coaching_note"].notna() & (openai["coaching_note"] != "")]

# Combine
combined = pd.concat([ollama_notes, openai_notes], ignore_index=True)

# Keep only relevant columns + add empty scoring columns
scoring = combined[[
    "model",
    "utterance_id",
    "language",
    "original_text",
    "translated_text",
    "label",
    "intensity",
    "ground_truth",
    "coaching_note",
]].copy()

scoring["tone_alignment"] = ""
scoring["actionability"] = ""

# Save
scoring.to_csv("src/evaluation/metric1_scoring_sheet.csv", index=False)
print(f"Saved {len(scoring)} rows to metric1_scoring_sheet.csv")
print(scoring[["model", "language", "label", "ground_truth"]].to_string())