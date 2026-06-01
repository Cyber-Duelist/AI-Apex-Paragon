import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score,confusion_matrix

print("=======1. LOADING DATA =======")
df = pd.read_csv("week_02/eda_project/data/document_reviews.csv")

X = df[['word_count', 'risk_score', 'review_time_hours' ]]
y = df['status']

print("========2. SPLITTING DATA==========")
X_train , X_test, y_train, y_test = train_test_split(X,y,test_size=0.2, random_state=42)

print("========3. TRADING THE AI (RANDOM FOREST)===========")
# random state =42 ensures that our random trees generate the same way very time
model = RandomForestClassifier(random_state=42)

# The AI builds 100 trees under the hood right now!
model.fit(X_train,y_train)
print("Rabdom Forest  trained successfully! \n")

print("========4. PREDICTING THE FUTURE=========")
predictions = model.predict(X_test)

results_df = pd.DataFrame({"Actual_Status": y_test,"AI_Prediction": predictions})
print(results_df.head())

print("\n=======5. GRADING THE AI=======")
accuracy = accuracy_score(y_test,predictions)
print(f"Accuracy: {accuracy*100:.2f}%")

print("\n=====6. CONFUSION MATRIX===========")
print("Rows = Actual, Columns = Predicted")
print(confusion_matrix(y_test,predictions))
