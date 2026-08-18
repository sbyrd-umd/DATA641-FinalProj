import pandas as pd

# Load labeled log
log = pd.read_csv("evaluation_log_labeled.csv")

results = []

# METRIC 2: Trigger Precision
log["expected_flagged"] = log["ground_truth"] == "hostile"
log["correct_trigger"] = log["flagged"] == log["expected_flagged"]

total = len(log)
correct = log["correct_trigger"].sum()
false_positives = len(log[(log["flagged"] == True) & (log["expected_flagged"] == False)])
false_negatives = len(log[(log["flagged"] == False) & (log["expected_flagged"] == True)])

results.append({"metric": "trigger_precision_overall_%", "language": "all", "category": "all", "value": round(correct / total * 100, 2)})
results.append({"metric": "false_positives", "language": "all", "category": "all", "value": false_positives})
results.append({"metric": "false_negatives", "language": "all", "category": "all", "value": false_negatives})

for lang, g in log.groupby("language"):
    results.append({"metric": "trigger_precision_%", "language": lang, "category": "all", "value": round(g["correct_trigger"].sum() / len(g) * 100, 2)})

for cat, g in log.groupby("ground_truth"):
    results.append({"metric": "trigger_precision_%", "language": "all", "category": cat, "value": round(g["correct_trigger"].sum() / len(g) * 100, 2)})

# METRIC 3: Latency
latency_rows = log[log["latency_ms"].notna() & (log["latency_ms"] != "")].copy()
latency_rows["latency_ms"] = pd.to_numeric(latency_rows["latency_ms"], errors="coerce")
latency_rows = latency_rows.dropna(subset=["latency_ms"])

results.append({"metric": "avg_latency_ms", "language": "all", "category": "all", "value": round(latency_rows["latency_ms"].mean(), 2)})
results.append({"metric": "min_latency_ms", "language": "all", "category": "all", "value": round(latency_rows["latency_ms"].min(), 2)})
results.append({"metric": "max_latency_ms", "language": "all", "category": "all", "value": round(latency_rows["latency_ms"].max(), 2)})


# METRIC 4: Cross-language Consistency
hostile_only = log[log["ground_truth"] == "hostile"]
for lang, g in hostile_only.groupby("language"):
    results.append({"metric": "hostile_flag_rate_%", "language": lang, "category": "hostile", "value": round(g["flagged"].sum() / len(g) * 100, 2)})

# Save
metrics_df = pd.DataFrame(results)
metrics_df.to_csv("metrics_ollama.csv", index=False)
print(metrics_df.to_string(index=False))
print("\nSaved to metrics_ollama.csv")