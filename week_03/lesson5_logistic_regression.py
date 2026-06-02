import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score,confusion_matrix,classification_report

print("====1. LOADING THE DATA====")
df = pd.read_csv("week_02/eda_project/data/document_reviews.csv")

print("=====2. CREATING CLASSIFICATION TARGET======")
df["needs_attention"] = (df['status'] != 'approved').astype(int)

print("Class distribution: ")
print(df['needs_attention'].value_counts())

X = df[["word_count", "risk_score", "review_time_hours", "category"]]
y = df["needs_attention"]

print("\n=====3. ONE HOT ENCODING CATEGORY=====")
X_encoded = pd.get_dummies(X,columns=['category'],drop_first=True)

print("Encoded feature columns:")
print(list(X_encoded.columns))

print("\n========4. SPLITTING THE DATA========")
X_train,X_test,y_train,y_test = train_test_split(X_encoded,y, test_size=0.4, random_state=42,stratify=y)

print(f"Training rows: {len(X_train)}")
print(f"Testing rows: {len(X_test)}")

print("\n=========5. TRAINING LOGISTIC REGRESSION MODEL========0")
model = LogisticRegression(max_iter=1000)
model.fit(X_train,y_train)
print("Model trained successfully.")

print("\n=======6. MAKING PREDICTIONS=======")
predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test)

results_df = pd.DataFrame({"actual": y_test.values,"predicted": predictions,"prob_approved": probabilities[:, 0],"prob_needs_attention": probabilities[:, 1],})
print(results_df)

print("\n========7. EVALUATION========")
accuracy = accuracy_score(y_test,predictions)
matrix = confusion_matrix(y_test,predictions)
report = classification_report(y_test,predictions)

print(f"Accuracy: {accuracy:.2f}%")
print("\n Confusion matrix:")
print(matrix)
print("\n Classification report:")
print(report)

print("\n=========8. LEARNED FEATURE WEIGHTS========")
for feature_name , coefficient in zip(X_encoded.columns,model.coef_[0]):
    print(f"{feature_name}: {coefficient:.4f}")

print(f"Intercept: {model.intercept_[0]:.4f}")    