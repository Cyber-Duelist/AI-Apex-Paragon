import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from xgboost import XGBClassifier
import joblib
import os

# 1. Load Data
# We use the user's specific B2C telecom dataset
DATA_PATH = r"C:\Users\adars\Downloads\customer_churn_dataset-training-master.csv"
print(f"Loading data from {DATA_PATH}...")
df = pd.read_csv(DATA_PATH)

# Drop missing values
df = df.dropna()

# 2. Define Features and Target
TARGET = "Churn"
# CustomerID is purely an identifier and shouldn't be used for ML training
FEATURES = [col for col in df.columns if col not in [TARGET, "CustomerID"]]

X = df[FEATURES]
y = df[TARGET]

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Build Preprocessing Pipeline
# Identify categorical and numerical columns dynamically based on the dataset
numeric_features = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
categorical_features = X.select_dtypes(include=['object', 'category']).columns.tolist()

print(f"Numeric features: {numeric_features}")
print(f"Categorical features: {categorical_features}")

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])

# 4. Define Model Pipeline
model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', XGBClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        eval_metric='logloss',
        use_label_encoder=False,
        random_state=42
    ))
])

# 5. Train Model
print("Training Telecom Churn Model...")
model_pipeline.fit(X_train, y_train)

# 6. Evaluate Accuracy (Optional sanity check)
train_acc = model_pipeline.score(X_train, y_train)
test_acc = model_pipeline.score(X_test, y_test)
print(f"Training Accuracy: {train_acc:.4f}")
print(f"Testing Accuracy: {test_acc:.4f}")

# 7. Save the Model Pipeline
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'telecom_model_pipeline.pkl')
joblib.dump(model_pipeline, OUTPUT_PATH)
print(f"Model successfully saved to {OUTPUT_PATH}")
