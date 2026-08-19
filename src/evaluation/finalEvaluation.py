import pandas as pd

# Load scoring sheet (metric 1)
scoring = pd.read_csv("src/evaluation/metric1_scoring_sheet.csv")
scoring["tone_alignment"] = pd.to_numeric(scoring["tone_alignment"], errors="coerce")
scoring["actionability"] = pd.to_numeric(scoring["actionability"], errors="coerce")

results = []

for model in ["ollama", "openai"]:
    model_scores = scoring[scoring["model"] == model]
    avg_tone = round(model_scores["tone_alignment"].mean(), 2)
    avg_action = round(model_scores["actionability"].mean(), 2)
    results.append({"metric": "tone_alignment_avg", "model": model, "language": "all", "category": "all", "value": avg_tone})
    results.append({"metric": "actionability_avg", "model": model, "language": "all", "category": "all", "value": avg_action})

# Load metrics 2/3/4 for both models
for model, filename in [("ollama", "src/evaluation/metrics_ollama.csv"), ("openai", "src/evaluation/metrics_openai.csv")]:
    df = pd.read_csv(filename)
    df["model"] = model
    results.extend(df.to_dict("records"))

# Combine and save
final = pd.DataFrame(results)
final = final[["metric", "model", "language", "category", "value"]]
final.to_csv("src/evaluation/final_evaluation.csv", index=False)
print(final.to_string(index=False))
print("\nSaved to final_evaluation.csv")