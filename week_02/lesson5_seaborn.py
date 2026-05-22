import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

data = {
    "category": ["Criminal Procedure", "Civil Rights", "First Amendment", "Due Process", "Privacy"],
    "doc_count": [859, 415, 230, 180, 120],
    "avg_majority_vote": [7.2, 6.8, 6.6, 7.0, 7.1]
}

df = pd.DataFrame(data)
sns.barplot(data=df, x ="category", y= "doc_count")
plt.title("Supreme court cases by category")
plt.xticks(rotation=45, ha= "right")
plt.tight_layout()
plt.savefig("seaborn_chart.png")


pivot = df.set_index("category")[["doc_count", "avg_majority_vote"]]
sns.heatmap(pivot, annot=True, cmap="YlGnBu", fmt= ".0f")
plt.title("Document Activity Heatmap")
plt.tight_layout()
plt.savefig("heatmap.png")
plt.show()
