import pandas as pd
import joblib

print("=== LOADING MODEL ===")
# Wake the AI up from its frozen state
# It remembers exactly how to scale numbers, encode text, and predict!
model_path = "week_04/document_risk_prediction/risk_model.pkl"
pipeline = joblib.load(model_path)

print("=== PREDICTING ON NEW SAMPLES ===")
# We manually craft 3 brand new documents that the AI has never seen
new_documents = [
    {"word_count": 500, "risk_score": 2.0, "category": "HR"},        # Looks safe
    {"word_count": 4500, "risk_score": 9.5, "category": "Legal"},     # Looks highly risky
    {"word_count": 1200, "risk_score": 4.0, "category": "Finance"}    # Borderline
]

# Convert the raw dictionaries into a Pandas DataFrame
df_samples = pd.DataFrame(new_documents)

# Ask the AI to make a hard decision (0 or 1)
predictions = pipeline.predict(df_samples)

# Ask the AI how confident it is (gives a percentage)
# predict_proba returns two columns: [Probability of 0, Probability of 1]
# We use [:, 1] to grab only the probability of it being a 1 (High Risk)
probabilities = pipeline.predict_proba(df_samples)[:, 1]

# Print a beautiful table of the results
print(f"{'Sample':<10} {'Predicted_Label':<17} {'Risk_Probability_%':<20}")
print("-" * 50)

for i in range(len(new_documents)):
    # Convert the decimal probability (e.g., 0.831) to a percentage (83.1)
    prob_percent = probabilities[i] * 100
    print(f"{i:<10} {predictions[i]:<17} {prob_percent:.1f}")

print("\nPrediction pipeline working.")