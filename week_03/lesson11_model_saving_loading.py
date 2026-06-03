import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import f1_score

print("=== 1. LOADING DATA ===")
df = pd.read_csv("week_02/eda_project/data/document_reviews.csv")

# Binary target:
# approved -> 0
# pending/rejected -> 1
df["needs_attention"] = (df["status"] != "approved").astype(int)

X = df[["word_count", "risk_score", "review_time_hours", "category"]]
y = df["needs_attention"]

numeric_features = ["word_count", "risk_score", "review_time_hours"]
categorical_features = ["category"]

print("\n=== 2. BUILDING PIPELINE ===")

preprocessor = ColumnTransformer(
    transformers=[
        ("num", "passthrough", numeric_features),
        ("cat", OneHotEncoder(drop="first", handle_unknown="ignore"), categorical_features),
    ]
)

pipeline = Pipeline(
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
    stratify=y
)

print("\n=== 4. TRAINING PIPELINE ===")
pipeline.fit(X_train, y_train)

predictions = pipeline.predict(X_test)
f1 = f1_score(y_test, predictions, zero_division=0)

print(f"Test F1 before saving: {f1:.4f}")

print("\n=== 5. SAVING MODEL ===")

model_path = "week_03/document_attention_model.joblib"
joblib.dump(pipeline, model_path)

print(f"Model saved to: {model_path}")

print("\n=== 6. LOADING MODEL ===")

loaded_model = joblib.load(model_path)

print("Model loaded successfully.")

print("\n=== 7. TESTING LOADED MODEL ON NEW DOCUMENT ===")

new_document = pd.DataFrame([
    {
        "word_count": 2200,
        "risk_score": 82,
        "review_time_hours": 5.5,
        "category": "Legal",
    }
])

prediction = loaded_model.predict(new_document)[0]
probability = loaded_model.predict_proba(new_document)[0]

label = "needs_attention" if prediction == 1 else "approved"

print(f"Prediction: {label}")
print(f"Probability approved: {probability[0]:.4f}")
print(f"Probability needs_attention: {probability[1]:.4f}")