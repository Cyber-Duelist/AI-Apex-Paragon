from sentence_transformers import SentenceTransformer, util

# 1. Load the open-source embedding model
# all-MiniLM-L6-v2 maps text to a 384-dimensional dense vector space
model = SentenceTransformer('all-MiniLM-L6-v2')

# 2. Define our knowledge base (document snippets)
documents = [
    "Merger agreement between Company A and Company B",
    "Employee handbook updated for 2024",
    "Quarterly financial report Q1 2024",
    "Legal compliance violation notice",
    "Tax audit documentation for fiscal year 2023"
]

print("=== GENERATING EMBEDDINGS ===")
# 3. Convert text to embeddings (numbers)
embeddings = model.encode(documents)

# Print details for each document to understand the data structure
for i, (doc, emb) in enumerate(zip(documents, embeddings)):
    print(f"Doc {i+1}: {doc}")
    print(f"Shape : {emb.shape}")
    
    # Format the first 5 values so they are easy to read
    first_5 = [f"{val:.4f}" for val in emb[:5]]
    print(f"First 5 values: [{', '.join(first_5)}]\n")

print("=== SIMILARITY TO DOC 1 ===")
# 4. Compute cosine similarity 
# This measures the mathematical angle between the vectors. 
# 1.0 means identical direction (meaning), lower means less related.
cosine_scores = util.cos_sim(embeddings[0], embeddings)[0]

for i, score in enumerate(cosine_scores):
    print(f"Doc 1 vs Doc {i+1}: {score:.4f}")