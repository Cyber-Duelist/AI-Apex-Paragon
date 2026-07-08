import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import classification_report, accuracy_score
import xgboost as xgb

def train_churn_model():
    print("Loading dataset...")
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saas_customer_data.csv')
    df = pd.read_csv(data_path)
    
    # Drop identifier
    X = df.drop(columns=['company_id', 'churn'])
    y = df['churn']
    
    # Identify numerical and categorical columns
    numeric_features = ['company_size', 'mrr_usd', 'tenure_months', 'active_users', 
                        'api_calls_per_month', 'support_tickets_last_30d', 
                        'feature_adoption_rate', 'last_login_days_ago']
    categorical_features = ['industry', 'contract_type']
    
    print("Building preprocessing pipeline...")
    # Create preprocessing steps
    numeric_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown='ignore')
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])
    
    # Create the XGBoost Classifier
    # Scale pos weight because churn dataset is imbalanced (~9% churn rate)
    scale_pos_weight = (len(y) - sum(y)) / sum(y)
    
    model = xgb.XGBClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        scale_pos_weight=scale_pos_weight,
        use_label_encoder=False,
        eval_metric='logloss',
        random_state=42
    )
    
    # Create the full pipeline
    pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                               ('classifier', model)])
    
    # Split data
    print("Splitting data into train/test sets...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Train the pipeline
    print("Training XGBoost pipeline...")
    pipeline.fit(X_train, y_train)
    
    # Evaluate
    print("Evaluating model...")
    y_pred = pipeline.predict(X_test)
    print("\n--- Classification Report ---")
    print(classification_report(y_test, y_pred))
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    
    # Save the pipeline
    output_model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'churn_model_pipeline.pkl')
    joblib.dump(pipeline, output_model_path)
    print(f"\nModel pipeline saved to: {output_model_path}")

if __name__ == "__main__":
    train_churn_model()
