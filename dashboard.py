import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
cases = pd.read_csv(BASE / "data" / "cases.csv")

# Optional AI review file. Create outputs/ai_diagnosis.csv with columns:
# case_id, ai_root_cause, ai_confidence, human_decision, agreement
review_path = BASE / "outputs" / "ai_diagnosis.csv"

print("NetSage AI Dashboard")
print("====================")
print("Total cases:", len(cases))
print("\nCases by concept:")
print(cases["concept"].value_counts())

print("\nCases by severity:")
print(cases["severity"].value_counts())

if review_path.exists():
    review = pd.read_csv(review_path)
    merged = cases.merge(review, on="case_id", how="left")
    agreement = merged["agreement"].dropna()
    if len(agreement):
        rate = (agreement.astype(str).str.lower().eq("yes").mean()) * 100
        print(f"\nAI vs Human agreement: {rate:.1f}%")
    print("\nHuman decisions:")
    print(review["human_decision"].value_counts())
else:
    print("\nAI review file not found yet.")
    print("Run the diagnosis workflow and save outputs/ai_diagnosis.csv.")

plt.figure(figsize=(10, 5))
cases["concept"].value_counts().plot(kind="bar")
plt.title("NetSage AI – Issue Types")
plt.xlabel("Concept")
plt.ylabel("Number of Cases")
plt.tight_layout()
plt.show()

plt.figure(figsize=(7, 5))
cases["severity"].value_counts().plot(kind="bar")
plt.title("NetSage AI – Severity")
plt.xlabel("Severity")
plt.ylabel("Number of Cases")
plt.tight_layout()
plt.show()
