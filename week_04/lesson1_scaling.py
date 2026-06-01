import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

print("========1.LOADING DATA=========")
df = pd.read_csv("week_02/eda_project/data/document_reviews.csv")

X = df[['word_count', 'risk_score', 'review_time_hours']]
y = df['status']

print("========2. SPLITTING THE DATA ==========")
X_train, X_test,y_train,y_test = train_test_split(X,y,test_size = 0.2, random_state=42)

print("=======3. SCALING THE DATA ======")
scaler = StandardScaler()

# CRITICAL ML RULE : We only 'fit' (learn the math) on the training data.
# If we fit on the test data, the ai is cheating by peeking at the future!
X_train_scaled = scaler.fit_transform(X_train)

# For the test data we just 'tramsform' it using the rules learned from the train data.
X_test_scaled = scaler.transform(X_test)

# Seeing the difference
print(f"Before scaling (First Row): {X_train.iloc[0].values}")
print(f"After scaling (First Row): {X_train_scaled[0]}\n")

print("=========4. TRAINING & GRADING========")
model = LogisticRegression(max_iter=1000)
model.fit(X_train_scaled,y_train)

predictions = model.predict(X_test_scaled)
accuracy = accuracy_score(y_test,predictions)
print(f"Accuracy with scaled data: {accuracy*100:.2f}%")