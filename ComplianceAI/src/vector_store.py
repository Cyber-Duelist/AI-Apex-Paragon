import os
import chromadb
import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)
current_dir = os.path.dirname(os.path.abspath(__file__))
model = SentenceTransformer('all-MiniLM-L6-v2')


def get_collection(user_id: int = None):
    db_path = os.path.join(current_dir, 'chroma_db')
    client = chromadb.PersistentClient(path=db_path)
    collection_name = f'user_{user_id}' if user_id else 'default'
    return client.get_or_create_collection(name=collection_name)


def add_chunks(chunks, collection):
    if not chunks:
        return
    ids = [c['chunk_id'] for c in chunks]
    texts = [c['text'] for c in chunks]
    metadatas = [{'source': c['source'], 'page': c['page'], 'char_start': c['char_start'], 'char_end': c['char_end']} for c in chunks]
    embeddings = model.encode(texts).tolist()
    collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)


def search(query, collection, top_k=3, source_filter=None):
    query_embedding = model.encode([query]).tolist()
    query_kwargs = {'query_embeddings': query_embedding, 'n_results': top_k}
    if source_filter:
        query_kwargs['where'] = {'source': source_filter}
    results = collection.query(**query_kwargs)
    formatted = []
    if results and 'documents' in results and results['documents']:
        for i in range(len(results['documents'][0])):
            formatted.append({'text': results['documents'][0][i], 'metadata': results['metadatas'][0][i]})
    return formatted


def delete_collection(collection):
    existing = collection.get()
    if existing and existing['ids']:
        collection.delete(ids=existing['ids'])


def delete_document_chunks(collection, source_filename):
    """Delete all chunks for a specific document from the collection."""
    existing = collection.get(where={'source': source_filename})
    if existing and existing['ids']:
        collection.delete(ids=existing['ids'])
