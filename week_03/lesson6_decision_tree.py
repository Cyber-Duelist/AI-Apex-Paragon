import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score,confusion_matrix,classification_report

print("========1. LOADING DATA=========")
df = pd.read_csv("week_02/eda_project/data/document_reviews.csv")

# we create a binary target:
# approved -> 0
# pending/rejected -> 1
df["needs_attention"] = (df['status']!= 'approved').astype(int)

print("\nClass distribution:")
print(df['needs_attention'].value_counts())

# Features are the input columns that the model can us eto make decisions
X =  df[["word_count", "risk_score", "review_time_hours", "category"]]
# Target is the answer column the model is trying to predict
y = df['needs_attention']

# Decision trees need numbers, so text categories must become numbers.
X_encoded = pd.get_dummies(X,columns=['category'],drop_first=True)

print("\nEncoded feature columns: ")
print(list(X_encoded.columns))

print("\n=======2. Splitting the data=======")
X_train,X_test,y_train,y_test = train_test_split(X_encoded,y,test_size=0.2,random_state=42,stratify=y)

print(f"Training rows: {len(X_train)}")
print(f"Testing rows: {len(X_test)}")


print("\n=======3.TRAINING DECISION TREE=========")
# max_depth limits how many questions the tree can ask.
# this helps in reducing overfitting.
model = DecisionTreeClassifier(max_depth = 3, random_state=42)
model.fit(X_train,y_train)
print("Model trained successfully.")


print("\n===========4. MAKING PREDICTIONS========")
predictions = model.predict(X_test)

results_df = pd.DataFrame({"Actual": y_test.values, "Predicted": predictions,})
print(results_df)


print("\n========5. EVALUATION=======")
accuracy = accuracy_score(y_test,predictions)
matrix = confusion_matrix(y_test,predictions)
report = classification_report(y_test,predictions)

print(f"Accuracy: {accuracy:.2f}")
print("\nConfusion Matrix:")
print(matrix)
print("\nClassification Report:")
print(report)

print("\n=== 6. FEATURE IMPORTANCE ===")
# Feature importance tells us which columns  the tree relied on the most.
for feature_name,importance in zip(X_encoded.columns,model.feature_importances_):
    print(f"{feature_name}: {importance:.4f}")