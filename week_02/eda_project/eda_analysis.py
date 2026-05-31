import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 1. SETUP: Ensure our charts folder exists so we don't get errors when saving
os.makedirs('week_02/eda_project/charts', exist_ok=True)

# 2. LOAD DATA: Since you are running this from the repo root, we use the full relative path
file_path = "week_02/eda_project/data/document_reviews.csv"
df = pd.read_csv(file_path)

print("=====PANDAS INVESTIGATION=======")

# .shape tells you numberof rows and columns.
print(f"\n1.Shape of dataset: {df.shape}")

# .head() prints the first five rows so you can see what the data actually looks like
print("\n2. First 5 rows: ")
print(df.head())

# .isnull().sum() counts missing values in every column. Crucial for cleaning data.
print("\n3. Missing values per column: ")
print(df.isnull().sum())

# .value_counts() groups the data by category and counts them.
print("\n4. Category distribution: ")
print(df['category'].value_counts())

# .mean() gets the average. We select the 'word_count' column specifically.
print(f"\n5. Average word count: {df['word_count'].mean():.2f}")

print("======GROUPBY ANALYSIS======")
# .groupby() is incredibly powerful. It splits the data by 'category', 
# selects two specific numerical columns, and calculates the mean for each category.

Category_stats = df.groupby('category')[['risk_score', 'review_time_hours']].mean()
print(Category_stats)


print("=======GENERATING CHARTS========")
# Seaborn (sns) makes beautiful charts with one line of code.

# Chart 1: Category count (Bar chart)
plt.figure(figsize=(8,5))
sns.countplot(data=df, x='category', palette='viridis')
plt.title("Number of documents per category")
plt.savefig('week_02/eda_project/charts/1_category_count.png')
plt.close()


# Chart2: Average risk by category
plt.figure(figsize=(8,5)) # sets the canvas size

sns.barplot(data=df , x='category', y='risk_score', palette='Reds')
plt.title('Average risk score by category')
plt.savefig('week_02/eda_project/charts/2_avg_risk.png')
plt.close() # closes 


# Chart3: Word count vs review time (scatter plot)
plt.figure(figsize=(8,5))


sns.scatterplot(data=df, x='word_count', y='review_time_hours', hue='category', s=100)
plt.title('Wordcount vs Review time')
plt.savefig('week_02/eda_project/charts/3_word_count_vs_time.png')
plt.close()

print("EDA COMPLETE! check your 'charts' folder for images. ")



