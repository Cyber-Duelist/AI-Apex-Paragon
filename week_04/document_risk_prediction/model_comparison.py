import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

print("=== 1. LOADING DATA ===")
# Load the dataset (Make sure you have this CSV ready in the right folder!)
df = pd.read_csv("week_04/document_risk_prediction/data/document_risk_dataset.csv")

# X = Features (The clues: numeric and categorical)
X = df[['word_count', 'risk_score', 'category']]
# y = Target (The answer we want: 1 for high_risk, 0 for safe)
y = df['high_risk']

print("=== 2. SPLITTING DATA ===")
# Hide 20% of the data for the final exam
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("=== 3. BUILDING THE FACTORY PIPELINE ===")
# Step A: Tell the factory which columns are numbers and which are text
numeric_features = ['word_count', 'risk_score']
categorical_features = ['category']

# Step B: Set up the specific machines for each data type
# ColumnTransformer acts as the factory manager, routing data to the right machine
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),      # Squash the numbers
        ('cat', OneHotEncoder(drop='first'), categorical_features) # Turn text into 1s and 0s
    ])

print("=== 4. SETTING UP THE COMPETITORS ===")
# We create a dictionary to hold our 3 AI models
models = {
    "Logistic Regression": LogisticRegression(random_state=42),
    "Decision Tree": DecisionTreeClassifier(random_state=42),
    "Random Forest": RandomForestClassifier(random_state=42)
}

# We will store the final grades here
results = []

print("=== 5. LET THE BATTLES BEGIN ===")
# We loop through each of the 3 models one by one
for model_name, ai_model in models.items():
    print(f"\nTraining {model_name}...")
    
    # Bundle the factory assembly line (preprocessor) with the AI model
    # Data goes in -> gets cleaned -> goes to the AI
    pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                               ('classifier', ai_model)])
    
    # 1. Train the AI
    pipeline.fit(X_train, y_train)
    
    # 2. Predict the hidden test data
    predictions = pipeline.predict(X_test)
    
    # 3. Grade the AI on the single test
    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(y_test, predictions, zero_division=0)
    recall = recall_score(y_test, predictions, zero_division=0)
    f1 = f1_score(y_test, predictions, zero_division=0)
    
    # 4. The Truth Serum (Cross-Validation using F1 Score)
    # We test it 5 different times on 5 different shuffles to find the True Average
    cv_scores = cross_val_score(pipeline, X_train, y_train, cv=5, scoring='f1')
    cv_mean = cv_scores.mean()
    cv_std = cv_scores.std() # How much the scores bounced around (volatility)
    
    # Save the grades
    results.append({
        "Model": model_name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1,
        "CV Mean F1": cv_mean,
        "CV Std F1": cv_std
    })

print("\n=== 6. FINAL RESULTS TABLE ===")
# Turn the results into a beautiful Pandas DataFrame to read easily
results_df = pd.DataFrame(results)
print(results_df.to_string(index=False))

print("\n=== 7. DECLARING THE WINNER ===")
# Find the model with the highest Cross-Validation Mean F1 Score
best_model = results_df.loc[results_df['CV Mean F1'].idxmax()]
print(f"🏆 The Best Model is: {best_model['Model']} (CV F1: {best_model['CV Mean F1']:.4f})")