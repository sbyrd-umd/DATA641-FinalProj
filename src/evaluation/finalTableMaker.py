import pandas as pd
from difflib import SequenceMatcher


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


# Load files
log = pd.read_csv("evaluation_log.csv")
utterances = pd.read_csv("test_utterances.csv")

# Build a flat list of all (test_id, category, text, language) combos
test_rows = []
for _, row in utterances.iterrows():
    test_rows.append({"test_id": row["id"], "category": row["category"], "text": row["english"], "language": "en"})
    test_rows.append({"test_id": row["id"], "category": row["category"], "text": row["italian"], "language": "it"})
    test_rows.append({"test_id": row["id"], "category": row["category"], "text": row["spanish"], "language": "es"})

test_df = pd.DataFrame(test_rows)


def match_row(log_row):
    """Find the best matching test utterance for a log row."""
    lang = log_row["language"]
    original = str(log_row["original_text"])

    # Filter candidates by language
    candidates = test_df[test_df["language"] == lang]

    best_score = 0
    best_id = None
    best_category = None

    for _, candidate in candidates.iterrows():
        score = similarity(original, candidate["text"])
        if score > best_score:
            best_score = score
            best_id = candidate["test_id"]
            best_category = candidate["category"]

    return pd.Series({"test_id": best_id, "ground_truth": best_category, "match_score": round(best_score, 3)})


# Apply matching
log[["test_id", "ground_truth", "match_score"]] = log.apply(match_row, axis=1)

# Save result
log.to_csv("evaluation_log_labeled.csv", index=False)
print("Done. Rows labeled:", len(log))
print(log[["original_text", "language", "test_id", "ground_truth", "match_score"]].to_string())