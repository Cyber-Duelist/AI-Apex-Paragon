import pandas as pd
import numpy as np
import uuid
import os

# Set random seed for reproducibility
np.random.seed(42)

def generate_saas_churn_data(n_samples=5000):
    """
    Generates a realistic synthetic B2B SaaS dataset for churn prediction.
    """
    print(f"Generating {n_samples} customer records...")
    
    # 1. Company IDs
    company_ids = [str(uuid.uuid4())[:8] for _ in range(n_samples)]
    
    # 2. Categorical Features
    industries = np.random.choice(
        ['Healthcare', 'Finance', 'E-commerce', 'Technology', 'Manufacturing'], 
        size=n_samples, 
        p=[0.15, 0.25, 0.3, 0.2, 0.1]
    )
    
    # 3. Numerical Features
    # Tenure in months (skewed towards newer customers)
    tenure_months = np.random.exponential(scale=24, size=n_samples).astype(int) + 1
    tenure_months = np.clip(tenure_months, 1, 120)
    
    # Company size (employees)
    company_size = np.random.lognormal(mean=4, sigma=1.5, size=n_samples).astype(int)
    company_size = np.clip(company_size, 5, 10000)
    
    # MRR (Monthly Recurring Revenue) correlates slightly with company size
    mrr_usd = np.clip(np.random.normal(company_size * 10, 500), 50, 100000).round(2)
    
    # Contract type
    contract_types = np.random.choice(['Month-to-Month', '1 Year', '2 Year'], size=n_samples, p=[0.5, 0.3, 0.2])
    
    # Engagement metrics
    active_users = np.clip(np.random.normal(company_size * 0.4, company_size * 0.1), 1, company_size).astype(int)
    
    # Feature adoption rate (0.0 to 1.0)
    feature_adoption_rate = np.clip(np.random.normal(0.6, 0.2, size=n_samples), 0.0, 1.0)
    
    # API calls per month
    api_calls_per_month = np.random.exponential(scale=50000, size=n_samples).astype(int)
    
    # Support tickets last 30 days
    support_tickets = np.random.poisson(lam=2, size=n_samples)
    
    # Last login days ago
    last_login_days_ago = np.random.exponential(scale=10, size=n_samples).astype(int)
    last_login_days_ago = np.clip(last_login_days_ago, 0, 90)
    
    # 4. Generate Churn (Target Variable)
    # We create a logic where churn is higher if:
    # - Month-to-month contract
    # - Low feature adoption
    # - Many support tickets
    # - High days since last login
    # - Low tenure
    
    churn_prob = np.zeros(n_samples)
    
    # Baseline
    churn_prob += 0.1
    
    # Contract impact
    churn_prob += np.where(contract_types == 'Month-to-Month', 0.2, 0)
    churn_prob -= np.where(contract_types == '2 Year', 0.15, 0)
    
    # Feature adoption impact (low adoption increases churn)
    churn_prob += (1.0 - feature_adoption_rate) * 0.3
    
    # Support tickets impact
    churn_prob += (support_tickets > 5) * 0.2
    
    # Last login impact
    churn_prob += (last_login_days_ago > 14) * 0.25
    
    # Tenure impact (newer customers churn more)
    churn_prob += (tenure_months < 6) * 0.15
    churn_prob -= (tenure_months > 24) * 0.1
    
    # Add noise
    churn_prob += np.random.normal(0, 0.1, n_samples)
    churn_prob = np.clip(churn_prob, 0, 1)
    
    # Final classification
    churn = (churn_prob > 0.65).astype(int)
    
    # Create DataFrame
    df = pd.DataFrame({
        'company_id': company_ids,
        'industry': industries,
        'company_size': company_size,
        'mrr_usd': mrr_usd,
        'contract_type': contract_types,
        'tenure_months': tenure_months,
        'active_users': active_users,
        'api_calls_per_month': api_calls_per_month,
        'support_tickets_last_30d': support_tickets,
        'feature_adoption_rate': feature_adoption_rate.round(3),
        'last_login_days_ago': last_login_days_ago,
        'churn': churn
    })
    
    return df

if __name__ == "__main__":
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(output_dir, 'saas_customer_data.csv')
    
    df = generate_saas_churn_data(10000)
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    
    print(f"Dataset generated with shape {df.shape}")
    print(f"Overall Churn Rate: {df['churn'].mean():.2%}")
    print(f"Saved to: {output_file}")
