import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score , confusion_matrix

print("======1. LOADING DATA=========")
df = pd.read_csv("week_02/eda_project/data/document_reviews.csv")

# X = Features (The Clues). We use 3 numeric columns here.
X = df[['word_count', 'risk_score', 'review_time_hours']]

# y = Target ( The label we want to predict)
y = df['status']


print("\n========2. SPLITTING DATA===========")
X_train,X_test,y_train,y_test = train_test_split(X,y,test_size= 0.3, random_state=42)

print("\n=======3. TRAINING THE AI (CLASSIFICATION)=======")
# max_iter=1000 gives the AI enough time to figure out the math under the hood
model = LogisticRegression(max_iter=1000)
model.fit(X_train,y_train)
print("Classification model trained successfully! \n")

print("\n=========4. PREDICTIMG THE FUTURE========")
predictions = model.predict(X_test)

results_df = pd.DataFrame({"Actual_Status": y_test, "AI_Prediction": predictions})
print(results_df.head())

print("\n=========5. GRADING THE AI==========")
# accuracy_score simply checks: (Correct prediction/Total prediction )
accuracy = accuracy_score(y_test,predictions)
print(f"Accuracy: {accuracy * 100:.2f}")

print("\n======6. CONFUSION MATRIX=========")
print("Rows = Actual , Columns = Predicted")
print(confusion_matrix(y_test,predictions))