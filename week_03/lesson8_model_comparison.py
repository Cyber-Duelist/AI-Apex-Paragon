import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score


print("=== 1. LOADING DATA ===")
df = pd.read_csv("week_02/eda_project/data/document_reviews.csv")

# Binary target:
# approved -> 0
# pending/rejected -> 1
df["needs_attention"] = (df["status"] != "approved").astype(int)

# Features: numeric columns + category.
X = df[["word_count", "risk_score", "review_time_hours", "category"]]
y = df["needs_attention"]

# Convert category text into numeric columns.
X_encoded = pd.get_dummies(X, columns=["category"], drop_first=True)

print("\nEncoded feature columns:")
print(list(X_encoded.columns))

print("\n=== 2. SPLITTING DATA ===")
X_train, X_test, y_train, y_test = train_test_split(
    X_encoded,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print(f"Training rows: {len(X_train)}")
print(f"Testing rows: {len(X_test)}")

print("\n=== 3. DEFINING MODELS ===")

# We keep all models in a dictionary so we can loop over them.
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Decision Tree": DecisionTreeClassifier(max_depth=3, random_state=42),
    "Random Forest": RandomForestClassifier(
        n_estimators=100,
        max_depth=3,
        random_state=42
    ),
}

results = []


print("\n=== 4. TRAINING AND EVALUATING MODELS ===")

for model_name, model in models.items():
    print(f"\nTraining: {model_name}")

    # Train model on training data.
    model.fit(X_train, y_train)

    # Predict on test data.
    predictions = model.predict(X_test)

    # Calculate metrics.
    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(y_test, predictions, zero_division=0)
    recall = recall_score(y_test, predictions, zero_division=0)
    f1 = f1_score(y_test, predictions, zero_division=0)

    results.append({
        "model": model_name,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    })

results_df = pd.DataFrame(results)

print("\n=== 5. MODEL COMPARISON RESULTS ===")
print(results_df)

best_model = results_df.sort_values(by="f1", ascending=False).iloc[0]

print("\n=== 6. BEST MODEL BY F1 SCORE ===")
print(best_model)