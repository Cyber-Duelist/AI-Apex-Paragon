import pandas as pd

data = {
    "document": ["NDA", "Contract", "NDA", "Lease", "Contract", "NDA"],
    "category": ["Legal", "HR", "Legal", "Property", "HR", "Legal"],
    "year": [2024, 2024, 2025, 2025, 2025, 2026],
    "word_count": [1500, 3200, 1800, 800, 2900, 2100]
}

df = pd.DataFrame(data)
print(df)

pivot = pd.pivot_table(df, 
                       values="word_count",
                       index="category",
                       columns="year",
                       aggfunc="mean")
print(pivot)

pivot_filled = pivot.fillna(0)
print(pivot_filled)