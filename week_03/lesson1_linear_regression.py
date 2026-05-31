import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

print("====1. LOADING DATA=====")
df = pd.read_csv("week_02/eda_project/data/document_reviews.csv")

# X = What we know (features/inputs). We use double brackets because its 2d dataFrame.
X = df[['word_count', 'risk_score']]

# y = What we want our model to predict (Target). Single bracket because its one column (1d series)
y = df['review_time_hours']

print("=====2. SPLITTING DATA======")
# test_size=0.2 means 20% data is hidden for testin the model.
# random_state=42 is just a seed so we get the exact same random split every time we run it.
X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.2, random_state=42)

print(f"Training on {len(X_train)} rows. Testing on {len(X_test)} hidden rows. \n")

print("======3. TRAINING THE AI=====")
model = LinearRegression()
# .fit() is where the real machine learning happens. It looks at x_train and y_train and finds the pattern
model.fit(X_train,y_train)
print("Model trained successfully! \n")


print("=======4. PREDICTING THE FUTURE=========")
# Now we ask the model to predict the review time for the 20 % data it has never seen.
predictions = model.predict(X_test)

# puttimg the actual answers and ai prediction side by side to see how it did.
results_df = pd.DataFrame({"Actual_hours": y_test, "AI_prediction": predictions})
print(results_df.head())

print("=======5. GRADING THE AI (EVALUATION)========")
# How wrong was the AI on average
mae = mean_absolute_error(y_test,predictions)
rmse = np.sqrt(mean_squared_error(y_test,predictions))

print(f"Mean Absolute Error (MAE): {mae:.2f} hours")
print(f"Root Mean Squared Error (RMSE): {rmse:.2f} hours \n")

print("=======6. WHAT DID THE MODEL LEARN?======")
# identifying the exact formula that the AI learned
print(f"Intercept (base time): {model.intercept_:.4f}")
print(f"Weight for Word Count: {model.coef_[0]:.4f}")
print(f"Weight for Risk Score: {model.coef_[1]:.4f}")