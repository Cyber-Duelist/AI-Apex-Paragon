import pandas as pd
import joblib

MODEL_PATH = "week_03/document_attention_classifier/models/document_attention_model.joblib"

print("=== 1. LOADING SAVED MODEL ===")
model_pipeline = joblib.load(MODEL_PATH)

print("Model loaded successfully.")

print("\n=== 2. CREATING SAMPLE DOCUMENTS ===")

# These are new documents the model has not seen during training.
sample_documents = pd.DataFrame(
    [
        {
            "word_count": 2200,
            "risk_score": 82,
            "review_time_hours": 5.5,
            "category": "Legal",
        },
        {
            "word_count": 900,
            "risk_score": 25,
            "review_time_hours": 1.4,
            "category": "HR",
        },
        {
            "word_count": 3100,
            "risk_score": 91,
            "review_time_hours": 7.0,
            "category": "Finance",
        },
    ]
)

print(sample_documents)

print("\n=== 3. MAKING PREDICTIONS ===")

predictions = model_pipeline.predict(sample_documents)
probabilities = model_pipeline.predict_proba(sample_documents)

for index, document in sample_documents.iterrows():
    prediction = predictions[index]
    probability = probabilities[index]

    label = "needs_attention" if prediction == 1 else "approved"

    print(f"\nDocument {index + 1}")
    print(f"Category: {document['category']}")
    print(f"Word count: {document['word_count']}")
    print(f"Risk score: {document['risk_score']}")
    print(f"Prediction: {label}")
    print(f"Probability approved: {probability[0]:.4f}")
    print(f"Probability needs_attention: {probability[1]:.4f}")