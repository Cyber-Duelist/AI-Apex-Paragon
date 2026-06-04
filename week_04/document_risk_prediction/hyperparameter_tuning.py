import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

# === 1. LOAD THE DATA ===
print("=== 1. LOADING DATA ===")
df = pd.read_csv("week_04/document_risk_prediction/data/document_risk_dataset.csv")

# X = The clues the AI uses to guess (Word count, risk score, category)
X = df[['word_count', 'risk_score', 'category']]
# y = The final answer the AI is trying to predict (1 for High Risk, 0 for Safe)
y = df['high_risk']


# === 2. SPLIT THE DATA ===
print("=== 2. SPLITTING DATA ===")
# We hide 20% of the data to test the AI later, exactly like a final exam.
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


# === 3. BUILD THE FACTORY ASSEMBLY LINE (PIPELINE) ===
print("=== 3. BUILDING THE PIPELINE ===")
# Define which columns are numbers and which are text categories
numeric_features = ['word_count', 'risk_score']
categorical_features = ['category']

# Set up the cleaning machines: 
# StandardScaler squashes massive numbers down to a level playing field.
# OneHotEncoder turns human text (like 'Legal') into 1s and 0s for the AI.
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(drop='first'), categorical_features)
    ])

# Bundle the cleaning machines (preprocessor) and the AI (RandomForest) together.
# We explicitly name the AI step 'model' so we can target it later.
pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('model', RandomForestClassifier(random_state=42))
])


# === 4. DEFINE THE DIALS TO TWIST (HYPERPARAMETERS) ===
print("=== 4. SETTING UP THE GRID SEARCH ===")
# Here we give the AI a list of settings (knobs) to test out.
# The "model__" prefix tells the pipeline to apply these settings ONLY to the AI part.
param_grid = {
    'model__n_estimators': [50, 100, 200],   # How many total trees in the forest?
    'model__max_depth': [3, 5, None],        # How deep can each tree grow? (None = infinite)
    'model__min_samples_split': [2, 5, 10]   # Minimum documents needed to make a new branch rule
}


# === 5. BRUTE-FORCE TESTING (GRID SEARCH) ===
print("=== 5. TRAINING (TESTING EVERY COMBINATION)... ===")
# GridSearchCV is an arena. It will automatically test EVERY combination of the settings above.
# cv=5 means it will test each combination 5 different times (Cross-Validation).
# scoring='f1' means the ultimate winner is the one with the best F1 Score.
grid_search = GridSearchCV(pipeline, param_grid, cv=5, scoring='f1', n_jobs=-1)

#  the battles begins! (This trains the models)
grid_search.fit(X_train, y_train)


# === 6. DECLARE THE WINNER ===
print("\n=== 6. THE WINNING SETTINGS ===")
# Print the absolute best combination of dials the arena found
print(f"Best Parameters: {grid_search.best_params_}")
print(f"Best CV F1 Score: {grid_search.best_score_:.4f}")


# === 7. THE FINAL EXAM ===
print("\n=== 7. FINAL EXAM ON UNSEEN TEST DATA ===")
# Grab the absolute best AI model that survived the arena
best_ai = grid_search.best_estimator_

# Make it predict the hidden 20% test data
predictions = best_ai.predict(X_test)

# Grade the predictions
print(f"Test Accuracy:  {accuracy_score(y_test, predictions):.4f}")
print(f"Test Precision: {precision_score(y_test, predictions, zero_division=0):.4f}")
print(f"Test Recall:    {recall_score(y_test, predictions, zero_division=0):.4f}")
print(f"Test F1 Score:  {f1_score(y_test, predictions, zero_division=0):.4f}")

print("\n=== 8. FULL REPORT CARD ===")
print(classification_report(y_test, predictions, zero_division=0))