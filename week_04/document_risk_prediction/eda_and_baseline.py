import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

DATA_PATH = "week_04/document_risk_prediction/data/document_risk_dataset.csv"
CHARTS_DIR = "week_04/document_risk_prediction/charts"

print("=== 1. LOADING DATA ===")
df = pd.read_csv(DATA_PATH)

print("\nDataset shape:")
print(df.shape)

print("\nFirst 5 rows:")
print(df.head())

print("\nMissing values:")
print(df.isnull().sum())

print("\nTarget distribution:")
print(df["high_risk"].value_counts())

print("\nCategory distribution:")
print(df["category"].value_counts())

print("\nStatus distribution:")
print(df["status"].value_counts())

print("\n=== 2. SAVING EDA CHARTS ===")

plt.figure(figsize=(8, 5))
sns.countplot(data=df, x="high_risk")
plt.title("High Risk Class Distribution")
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/1_high_risk_distribution.png")
plt.close()

plt.figure(figsize=(10, 5))
sns.countplot(data=df, x="category", hue="high_risk")
plt.title("High Risk by Category")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/2_high_risk_by_category.png")
plt.close()

plt.figure(figsize=(8, 5))
sns.scatterplot(data=df, x="risk_score", y="review_time_hours", hue="high_risk")
plt.title("Risk Score vs Review Time")
plt.tight_layout()
plt.savefig(f"{CHARTS_DIR}/3_risk_vs_review_time.png")
plt.close()

print("Charts saved.")

print("\n=== 3. BUILDING FEATURES AND TARGET ===")

numeric_features = [
    "word_count",
    "risk_score",
    "review_time_hours",
    "contains_sensitive_terms",
    "external_party_count",
    "revision_count",
]

categorical_features = ["category", "status"]

X = df[numeric_features + categorical_features]
y = df["high_risk"]

print("\nNumeric features:")
print(numeric_features)

print("\nCategorical features:")
print(categorical_features)

print("\n=== 4. BUILDING PREPROCESSING PIPELINE ===")

numeric_transformer = Pipeline(
    steps=[
        ("scaler", StandardScaler())
    ]
)

categorical_transformer = Pipeline(
    steps=[
        ("onehot", OneHotEncoder(drop="first", handle_unknown="ignore"))
    ]
)

preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric_transformer, numeric_features),
        ("cat", categorical_transformer, categorical_features),
    ]
)

baseline_model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", LogisticRegression(max_iter=1000))
    ]
)

print("Baseline pipeline created.")

print("\n=== 5. TRAIN/TEST SPLIT ===")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print(f"Training rows: {len(X_train)}")
print(f"Testing rows: {len(X_test)}")

print("\n=== 6. TRAINING BASELINE MODEL ===")
baseline_model.fit(X_train, y_train)

print("Baseline model trained.")

print("\n=== 7. EVALUATING BASELINE MODEL ===")
predictions = baseline_model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)
precision = precision_score(y_test, predictions, zero_division=0)
recall = recall_score(y_test, predictions, zero_division=0)
f1 = f1_score(y_test, predictions, zero_division=0)

print(f"Accuracy: {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1: {f1:.4f}")

print("\nClassification Report:")
print(classification_report(y_test, predictions, zero_division=0))

print("\n=== 8. CROSS-VALIDATION ===")

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

cv_scores = cross_val_score(
    baseline_model,
    X,
    y,
    cv=cv,
    scoring="f1"
)

print(f"Fold F1 scores: {cv_scores}")
print(f"Mean F1: {cv_scores.mean():.4f}")
print(f"Std F1: {cv_scores.std():.4f}")