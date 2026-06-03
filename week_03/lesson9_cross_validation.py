import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score

print("=== 1. LOADING DATA ===")
df = pd.read_csv("week_02/eda_project/data/document_reviews.csv")

# Binary target:
# approved -> 0
# pending/rejected -> 1
df["needs_attention"] = (df["status"] != "approved").astype(int)

X = df[["word_count", "risk_score", "review_time_hours", "category"]]
y = df["needs_attention"]

# Convert category text to numeric 0/1 columns.
X_encoded = pd.get_dummies(X, columns=["category"], drop_first=True)

print("\nEncoded feature columns:")
print(list(X_encoded.columns))

print("\n=== 2. DEFINING MODELS ===")
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Decision Tree": DecisionTreeClassifier(max_depth=3, random_state=42),
    "Random Forest": RandomForestClassifier(
        n_estimators=100,
        max_depth=3,
        random_state=42
    ),
}

# StratifiedKFold keeps class balance in each fold.
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

results = []

print("\n=== 3. CROSS-VALIDATION RESULTS ===")

for model_name, model in models.items():
    scores = cross_val_score(
        model,
        X_encoded,
        y,
        cv=cv,
        scoring="f1"
    )

    mean_score = scores.mean()
    std_score = scores.std()

    results.append({
        "model": model_name,
        "mean_f1": mean_score,
        "std_f1": std_score,
        "fold_scores": scores,
    })

    print(f"\n{model_name}")
    print(f"Fold F1 scores: {scores}")
    print(f"Mean F1: {mean_score:.4f}")
    print(f"Std F1: {std_score:.4f}")

results_df = pd.DataFrame(results)

print("\n=== 4. SUMMARY TABLE ===")
print(results_df[["model", "mean_f1", "std_f1"]])

best_model = results_df.sort_values(by="mean_f1", ascending=False).iloc[0]

print("\n=== 5. BEST MODEL BY CROSS-VALIDATED F1 ===")
print(best_model[["model", "mean_f1", "std_f1"]])