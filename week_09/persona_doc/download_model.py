import chromadb
from chromadb.utils import embedding_functions

print("Downloading ONNX embedding model during build phase...")
ef = embedding_functions.DefaultEmbeddingFunction()
# This triggers the download
ef(["warmup"])
print("Model downloaded and cached successfully.")
