import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
)

DATA_PATH = "week_02/eda_project/data/document_reviews.csv"
MODEL_PATH = "week_03/document_attention_classifier/models/document_attention_model.joblib"

print("=== 1. LOADING DATA ===")
df = pd.read_csv(DATA_PATH)

# Target:
# approved -> 0
# pending/rejected -> 1
df["needs_attention"] = (df["status"] != "approved").astype(int)

# Features are the inputs the model uses to make predictions.
X = df[["word_count", "risk_score", "review_time_hours", "category"]]

# Target is the answer the model learns to predict.
y = df["needs_attention"]

numeric_features = ["word_count", "risk_score", "review_time_hours"]
categorical_features = ["category"]

print("Class distribution:")
print(y.value_counts())

print("\n=== 2. BUILDING PIPELINE ===")

# Numeric columns are already numbers, so we pass them through unchanged.
# Category is text, so we convert it into one-hot encoded columns.
preprocessor = ColumnTransformer(
    transformers=[
        ("num", "passthrough", numeric_features),
        ("cat", OneHotEncoder(drop="first", handle_unknown="ignore"), categorical_features),
    ]
)

# The pipeline keeps preprocessing and model training together.
model_pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", LogisticRegression(max_iter=1000)),
    ]
)

print("Pipeline created.")

print("\n=== 3. SPLITTING DATA ===")
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)

print(f"Training rows: {len(X_train)}")
print(f"Testing rows: {len(X_test)}")

print("\n=== 4. TRAINING MODEL ===")
model_pipeline.fit(X_train, y_train)
print("Model trained successfully.")

print("\n=== 5. EVALUATING MODEL ===")
predictions = model_pipeline.predict(X_test)

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

print("\n=== 6. SAVING MODEL ===")

# Save the full pipeline, not only the model.
# This preserves preprocessing for future predictions.
joblib.dump(model_pipeline, MODEL_PATH)

print(f"Model saved to: {MODEL_PATH}")