import matplotlib.pyplot as plt
import pandas as pd


categories = ["Criminal Procedure", "Civil Rights", "First Amendment", "Due Process", "Privacy"]
doc_counts = [859, 415, 230, 180, 120]

plt.figure(figsize=(12,6))
plt.bar(categories,doc_counts)
plt.title("court chart")
plt.xlabel("categories")
plt.ylabel("doc_counts")
plt.xticks(rotation=45, ha='right')
plt.bar(categories, doc_counts, color='steelblue')
plt.tight_layout()
plt.savefig("supreme_court_categories.png")
plt.show()
