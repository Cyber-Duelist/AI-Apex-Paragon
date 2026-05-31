import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os


os.makedirs('week_02/eda_project/charts', exist_ok=True)


file_path = "week_02/eda_project/data/document_reviews.csv"
df = pd.read_csv(file_path)

print("=====PANDAS INVESTIGATION=======")

print(f"\n1.Shape of dataset: {df.shape}")

print("\n2. First 5 rows: ")
print(df.head())


print("\n3. Missing values per column: ")
print(df.isnull().sum())


print("\n4. Category distribution: ")
print(df['category'].value_counts())


print(f"\n5. Average word count: {df['word_count'].mean():.2f}")

print("======GROUPBY ANALYSIS======")


Category_stats = df.groupby('category')[['risk_score', 'review_time_hours']].mean()
print(Category_stats)


print("=======GENERATING CHARTS========")

# Chart 1: Category count (Bar chart)
plt.figure(figsize=(8,5))
sns.countplot(data=df, x='category', palette='viridis')
plt.title("Number of documents per category")
plt.savefig('week_02/eda_project/charts/1_category_count.png')
plt.close()


# Chart2: Average risk by category
plt.figure(figsize=(8,5))

sns.barplot(data=df , x='category', y='risk_score', palette='Reds')
plt.title('Average risk score by category')
plt.savefig('week_02/eda_project/charts/2_avg_risk.png')
plt.close()


# Chart3: Word count vs review time (scatter plot)
plt.figure(figsize=(8,5))


sns.scatterplot(data=df, x='word_count', y='review_time_hours', hue='category', s=100)
plt.title('Wordcount vs Review time')
plt.savefig('week_02/eda_project/charts/3_word_count_vs_time.png')
plt.close()

print("EDA COMPLETE! check your 'charts' folder for images. ")



