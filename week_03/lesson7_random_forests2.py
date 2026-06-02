import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score,confusion_matrix,classification_report

print("=== 1. LOADING DATA ===")
df = pd.read_csv("week_02/eda_project/data/document_reviews.csv")

# Create a binary classification target:
# approved -> 0
# pending/rejected -> 1
df['needs_attention'] = (df['status']!='approved').astype(int)

print("\nClass distribution:")
print(df['needs_attention'].value_counts())

# Input features.
X = df[["word_count", "risk_score", "review_time_hours", "category"]]

# Target label.
y = df["needs_attention"]

# Convert text category into numeric 0/1 columns.
X_encoded = pd.get_dummies(X, columns=['category'],drop_first=True)

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

print("\n=== 3. TRAINING RANDOM FOREST ===")

# n_estimators = number of decision trees.
# max_depth limits tree complexity.
# random_state keeps results reproducible.
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=3,
    random_state=42
)

model.fit(X_train, y_train)

print("Model trained successfully.")

print("\n=======4. MAKING PREDICTIONS=======")
predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test)

results_df = pd.DataFrame({
    "actual": y_test.values,
    "predicted": predictions,
    "prob_approved": probabilities[:, 0],
    "prob_needs_attention": probabilities[:, 1],
})
print(results_df)

print("\n=== 5. EVALUATION ===")
accuracy = accuracy_score(y_test, predictions)
matrix = confusion_matrix(y_test, predictions)
report = classification_report(y_test, predictions)
print(f"Accuracy: {accuracy:.2f}")
print("\nConfusion Matrix:")
print(matrix)
print("\nClassification Report:")
print(report)


print("\n======6. FEATURE IMPORTANCES=======")
for feature_name,importance in zip(X_encoded.columns,model.feature_importances_):
    print(f"{feature_name}: {importance:.4f}")