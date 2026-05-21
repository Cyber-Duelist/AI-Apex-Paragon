import pandas as pd
docs = pd.DataFrame({
    "document_name": ["NDA_2026", "Employment_Contract", "Lease_Agreement", "Privacy_Policy", "Patent_Filing"],
    "word_count": [1500, 3200, 800, 1200, 2500]
})

categories = pd.DataFrame({
    "document_name": ["NDA_2026", "Employment_Contract", "Lease_Agreement"],
    "category": ["Confidentiality", "HR", "Property"]
})

merged = pd.merge(docs,categories,on="document_name",how="left")
print(merged)