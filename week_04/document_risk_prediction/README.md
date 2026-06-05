# Document Risk Prediction

A machine learning project that predicts whether a document is high-risk based on its metadata and content features.

---

## Problem Statement

Organizations process hundreds of documents daily — contracts, reports, submissions. Manually flagging risky ones is slow and inconsistent. This project builds a classifier that automatically identifies high-risk documents so reviewers can focus their attention where it matters most.

---

## Dataset

- **Source:** Generated using `generate_dataset.py`
- **Size:** 80 rows
- **Target:** `high_risk` (1 = high risk, 0 = low risk)
- **Numeric features:** `num_pages`, `word_count`, `revision_count`, `days_since_last_edit`, `num_authors`
- **Categorical features:** `document_type`, `department`, `sensitivity_level`

---

## Project Structure

```
week_04/document_risk_prediction/
│
├── generate_dataset.py       # Creates the synthetic dataset (80 rows)
├── baseline.py               # First model - Logistic Regression, no tuning
├── model_comparison.py       # Compares Logistic Regression, Decision Tree, Random Forest
├── hyperparameter_tuning.py  # GridSearchCV on Random Forest to find best settings
├── save_model.py             # Trains final model on full data and saves it to disk
├── predict.py                # Loads saved model and predicts on new document samples
├── document_risk_dataset.csv # The generated dataset
├── risk_model.pkl            # The saved production model
└── README.md                 # This file
```

---

## ML Pipeline

```
Raw CSV
  → Preprocessing (StandardScaler for numbers, OneHotEncoder for categories)
  → Baseline (Logistic Regression, quick sanity check)
  → Model Comparison (3 models, cross-validation F1)
  → Hyperparameter Tuning (GridSearchCV on best candidate)
  → Save Model (joblib, full dataset)
  → Predict (load pkl, run on new samples)
```

---

## Results

### Model Comparison (Cross-Validation F1)

| Model               | CV Mean F1 |
|---------------------|------------|
| Logistic Regression | 0.6333     |
| Decision Tree       | 0.5962     |
| Random Forest       | 0.4365     |

> Logistic Regression won the CV comparison — simpler models can generalise better on small datasets.

### Best Tuned Model — Random Forest (GridSearchCV)

| Metric    | Score  |
|-----------|--------|
| Accuracy  | 0.8750 |
| Precision | 0.6667 |
| Recall    | 1.0000 |
| F1 Score  | 0.8000 |

Best parameters: `max_depth=5`, `min_samples_split=5`, `n_estimators=200`

> Tuning pushed Random Forest's test F1 from ~0.73 to 0.80 — a meaningful gain on unseen data.

---

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Generate dataset
python generate_dataset.py

# Run the full pipeline
python baseline.py
python model_comparison.py
python hyperparameter_tuning.py
python save_model.py
python predict.py
```

---

## Key Learnings

- Cross-validation F1 is more trustworthy than a single test split — a model can look great on one split and fall apart on another.
- Simpler models (Logistic Regression) can outperform complex ones when data is small; complexity needs data to pay off.
- Saving a full sklearn Pipeline (preprocessor + model together) means prediction on new data just works — no manual feature transformation needed.

---

## Tech Stack

`Python` · `scikit-learn` · `pandas` · `joblib`