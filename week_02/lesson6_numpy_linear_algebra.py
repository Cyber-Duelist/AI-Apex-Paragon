import numpy as np

#1 Creating the two vectors
query_embedding = np.array([0.2, 0.4, 0.6])
document_embedding = np.array([0.1, 0.5, 0.7])

#2 Getting the vector shapes
query_shape = query_embedding.shape
document_shape = document_embedding.shape

#3 Calculating dot product
dot_product = query_embedding @ document_embedding

#4 Claculate vector norms/magnitude
query_norm = np.linalg.norm(query_embedding)
document_norm = np.linalg.norm(document_embedding)

#5 Calculate cosine similiarity
cosine_similarity = dot_product /(query_norm*document_norm)

print(f"Query embedding shape: {query_shape}")
print(f"Document embedding shape: {document_shape}")
print(f"Dot product: {dot_product:.4f}")
print(f"Query magnitude: {query_norm:.4f} ")
print(f"Document magnitude: {document_norm:.4f}")
print(f"Cosine_similiarity: {cosine_similarity:.4f}")


# Task 2
features = np.array([
    [1500, 3],
    [3200, 5],
    [800, 1]
])
weights = np.array([0.01, 2])
scores = features @ weights
print(f"Document scores: {scores}")