import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

print("=== 1. LOADING FULL DATASET ===")
# We load the entire dataset. No hiding 20% this time!
df = pd.read_csv("week_04/document_risk_prediction/data/document_risk_dataset.csv")

X = df[['word_count', 'risk_score', 'category']]
y = df['high_risk']

print("=== 2. BUILDING THE FACTORY PIPELINE ===")
numeric_features = ['word_count', 'risk_score']
categorical_features = ['category']

# The cleaning machines
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(drop='first'), categorical_features)
    ])

# The AI Brain (using the winning settings from Pack 4)
pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('model', RandomForestClassifier(
        max_depth=5, 
        min_samples_split=5, 
        n_estimators=200, 
        random_state=42
    ))
])

print("=== 3. TRAINING THE FINAL PRODUCTION MODEL ===")
# Train the pipeline on ALL available data
pipeline.fit(X, y)

print("=== 4. SHRINK-WRAPPING AND SAVING TO DISK ===")
# joblib.dump takes the trained pipeline and saves it as a physical file
file_path = "week_04/document_risk_prediction/risk_model.pkl"
joblib.dump(pipeline, file_path)

print(f"Model successfully saved to {file_path}")