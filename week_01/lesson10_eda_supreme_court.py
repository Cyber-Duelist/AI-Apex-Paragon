import pandas as pd
df = pd.read_csv("justice.csv")
print(df.head())
print(df.shape)
print(df.info())

df_clean = df.dropna(subset = ["issue_area"])
print(df_clean.shape)
print(df_clean["issue_area"].value_counts())
print(df_clean.groupby("issue_area")["majority_vote"].mean())

import matplotlib.pyplot as plt

df_clean["issue_area"].value_counts().plot(kind="bar", figsize=(12,6))
plt.title("Supreme Court Cases by Issue Area")
plt.xlabel("Issue Area")
plt.ylabel("Number of Cases")
plt.tight_layout()
plt.savefig("supreme_court_eda.png")
plt.show()