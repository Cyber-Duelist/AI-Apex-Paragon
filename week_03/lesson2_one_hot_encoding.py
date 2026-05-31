import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, root_mean_squared_error # <-- NEW IMPORT

print("=== 1. LOADING & PREPARING DATA ===")
# Load the data
df = pd.read_csv("week_02/eda_project/data/document_reviews.csv")

# X = Features (Now including text!)
X = df[["word_count", "risk_score", "category"]]
y = df["review_time_hours"]

print("Original Features (First 3 rows):")
print(X.head(3))

# ONE-HOT ENCODING: The Translation
# We tell Pandas to take the 'category' column and split it into 1s and 0s.
X_encoded = pd.get_dummies(X, columns=["category"], drop_first=True)

print("\nEncoded Features (First 3 rows):")
print(X_encoded.head(3))

print("\n=== 2. SPLITTING DATA ===")
# We use X_encoded instead of X because the AI needs the 1s and 0s!
X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)

print("=== 3. TRAINING THE AI ===")
model = LinearRegression()
model.fit(X_train, y_train)

print("=== 4. PREDICTING THE FUTURE ===")
predictions = model.predict(X_test)

results_df = pd.DataFrame({
    "Actual_Hours": y_test,
    "AI_Prediction": predictions
})
print(results_df.head())

print("\n=== 5. GRADING THE AI ===")
mae = mean_absolute_error(y_test, predictions)
rmse = root_mean_squared_error(y_test, predictions) # <-- CLEANER RMSE
print(f"MAE: {mae:.2f} hours")
print(f"RMSE: {rmse:.2f} hours")

print("\n=== 6. THE AI'S LEARNED WEIGHTS ===")
print(f"Intercept (Baseline Time): {model.intercept_:.4f}")

# zip() pairs up the names of our columns with the weights the AI learned
for feature_name, coefficient in zip(X_encoded.columns, model.coef_):
    print(f"{feature_name}: {coefficient:.4f}")