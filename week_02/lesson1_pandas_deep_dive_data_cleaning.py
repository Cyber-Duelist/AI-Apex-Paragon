import pandas as pd
import numpy as np

data = {
    "document_name": ["NDA_2026", "Employment_Contract", "NDA_2026", "Lease_Agreement", "Privacy_Policy", None],
    "category": ["Legal", "legal", "Legal", "LEGAL", "Legal", "Legal"],
    "word_count": [1500, 3200, 1500, None, 800, 1200],
    "review_date": ["2026-01-15", "2026/02/20", "2026-01-15", "20-03-2026", "2026-04-10", "2026-05-01"]
}

df = pd.DataFrame(data)
print(df)

# Step 1 Remove duplicates
df_clean = df.drop_duplicates()
print(df_clean.shape)

# Step 2 Handling missing values
df_missing = df_clean.dropna(subset = ["document_name"] ).copy()
print(df_missing)

# Step 2b Fill the missing word_count
df_missing["word_count"] = df_missing["word_count"].fillna(df_missing["word_count"].mean())
print(df_missing["word_count"])

# Step 3 Fixing inconsistent category casing
df_missing["category"] = df_missing["category"].str.lower()
print(df_missing["category"])

# Step 4 Fixing date formats
df_missing["review_date"] = pd.to_datetime(df_missing["review_date"],format = 'mixed', dayfirst = True)
print(df_missing["review_date"])