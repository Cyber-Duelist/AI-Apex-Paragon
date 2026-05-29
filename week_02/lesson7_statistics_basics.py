import numpy as np

# 1. Define the data
word_counts = np.array([1500, 3200, 800, 1200, 2500, 1800])
review_times = np.array([3, 7, 2, 4, 6, 5])

# 2. Calculate statistics for word_counts
mean_wc = np.mean(word_counts)
median_wc = np.median(word_counts)
std_wc = np.std(word_counts)
min_wc = np.min(word_counts)
max_wc = np.max(word_counts)

# 3. Calculate correlation between the two arrays
# np.corrcoef returns a 2x2 correlation matrix. 
# The value at [0, 1] (or [1, 0]) is the correlation between the two variables.
correlation_matrix = np.corrcoef(word_counts, review_times)
correlation = correlation_matrix[0, 1]

# 4. Print the results
print("=== Word Count Statistics ===")
print(f"Mean (Average):     {mean_wc:.2f}")
print(f"Median (Middle):    {median_wc:.2f}")
print(f"Standard Deviation: {std_wc:.2f}")
print(f"Minimum:            {min_wc}")
print(f"Maximum:            {max_wc}\n")

print("=== Relationship ===")
print(f"Correlation between word counts and review times: {correlation:.4f}")