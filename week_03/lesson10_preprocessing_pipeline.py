import pandas as pd

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

print("=== 1. LOADING DATA ===")
df = pd.read_csv("week_02/eda_project/data/document_reviews.csv")

# Create binary target:
# approved -> 0
# pending/rejected -> 1
df["needs_attention"] = (df["status"] != "approved").astype(int)

# Raw features. Notice category stays as text here.
X = df[["word_count", "risk_score", "review_time_hours", "category"]]
y = df["needs_attention"]

numeric_features = ["word_count", "risk_score", "review_time_hours"]
categorical_features = ["category"]

print("\nNumeric features:")
print(numeric_features)

print("\nCategorical features:")
print(categorical_features)

print("\n=== 2. BUILDING PREPROCESSOR ===")

# ColumnTransformer lets us apply different transformations to different columns.
# Here, numeric columns pass through unchanged.
# Category is converted into one-hot encoded columns.
preprocessor = ColumnTransformer(
    transformers=[
        ("num", "passthrough", numeric_features),
        ("cat", OneHotEncoder(drop="first", handle_unknown="ignore"), categorical_features),
    ]
)

print("Preprocessor created.")

print("\n=== 3. BUILDING PIPELINE ===")

# The pipeline first preprocesses raw data, then trains Logistic Regression.
pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", LogisticRegression(max_iter=1000)),
    ]
)

print("Pipeline created.")

print("\n=== 4. SPLITTING DATA ===")
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print(f"Training rows: {len(X_train)}")
print(f"Testing rows: {len(X_test)}")

print("\n=== 5. TRAINING PIPELINE ===")
pipeline.fit(X_train, y_train)

print("Pipeline trained successfully.")

print("\n=== 6. MAKING PREDICTIONS ===")
predictions = pipeline.predict(X_test)

results_df = pd.DataFrame({
    "actual": y_test.values,
    "predicted": predictions,
})

print(results_df)

print("\n=== 7. EVALUATION ===")
accuracy = accuracy_score(y_test, predictions)
precision = precision_score(y_test, predictions, zero_division=0)
recall = recall_score(y_test, predictions, zero_division=0)
f1 = f1_score(y_test, predictions, zero_division=0)

print(f"Accuracy: {accuracy:.2f}")
print(f"Precision: {precision:.2f}")
print(f"Recall: {recall:.2f}")
print(f"F1: {f1:.2f}")

print("\nClassification Report:")
print(classification_report(y_test, predictions, zero_division=0))

print("\n=== 8. CROSS-VALIDATION WITH PIPELINE ===")
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

cv_scores = cross_val_score(
    pipeline,
    X,
    y,
    cv=cv,
    scoring="f1"
)

print(f"Fold F1 scores: {cv_scores}")
print(f"Mean F1: {cv_scores.mean():.4f}")
print(f"Std F1: {cv_scores.std():.4f}")