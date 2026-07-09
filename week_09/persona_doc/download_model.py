import os
import chromadb
from chromadb.utils import embedding_functions

# Force HuggingFace to download the model into a local folder that gets bundled into the Render snapshot
os.environ["HF_HOME"] = os.path.join(os.path.dirname(__file__), ".hf_cache")

print("Downloading ONNX embedding model during build phase...")
ef = embedding_functions.DefaultEmbeddingFunction()
# This triggers the download
ef(["warmup"])
print("Model downloaded and cached successfully.")
