import random
from pathlib import Path

import pandas as pd

random.seed(42)

OUTPUT_PATH = Path("week_04/document_risk_prediction/data/document_risk_dataset.csv")

categories = ["Legal", "HR", "Finance", "Privacy", "Technical", "Compliance"]
statuses = ["approved", "pending", "rejected", "escalated"]

rows = []

for i in range(1, 81):
    category = random.choice(categories)

    word_count = random.randint(600, 6000)
    review_time_hours = round(random.uniform(0.8, 10.0), 1)
    risk_score = random.randint(10, 100)
    contains_sensitive_terms = random.choice([0, 0, 0, 1, 1])
    external_party_count = random.randint(0, 8)
    revision_count = random.randint(0, 6)

    risk_points = 0

    if risk_score >= 75:
        risk_points += 2
    elif risk_score >= 55:
        risk_points += 1

    if contains_sensitive_terms == 1:
        risk_points += 2

    if external_party_count >= 5:
        risk_points += 1

    if revision_count >= 4:
        risk_points += 1

    if review_time_hours >= 6:
        risk_points += 1

    if category in ["Legal", "Privacy", "Compliance"]:
        risk_points += 1

    # Add a little noise so the dataset is not too perfect.
    if random.random() < 0.12:
        risk_points -= 1

    high_risk = 1 if risk_points >= 4 else 0

    if high_risk == 1:
        status = random.choice(["pending", "rejected", "escalated", "escalated"])
    else:
        status = random.choice(["approved", "approved", "pending"])

    rows.append(
        {
            "document_id": f"DOC{i:03d}",
            "category": category,
            "word_count": word_count,
            "review_time_hours": review_time_hours,
            "risk_score": risk_score,
            "contains_sensitive_terms": contains_sensitive_terms,
            "external_party_count": external_party_count,
            "revision_count": revision_count,
            "status": status,
            "high_risk": high_risk,
        }
    )

df = pd.DataFrame(rows)

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False)

print(f"Saved dataset to {OUTPUT_PATH}")
print(f"Dataset shape: {df.shape}")
print("\nFirst 10 rows:")
print(df.head(10))
print("\nClass distribution:")
print(df["high_risk"].value_counts())