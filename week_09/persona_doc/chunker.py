import os
import sys

# Ensure Python can find ingest.py if we run this from the root directory
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from ingest import ingest_document

def chunk_document(pages: list[dict], chunk_size: int = 400, overlap: int = 80) -> list[dict]:
    """
    Takes a list of page dictionaries and splits the text into fixed-size chunks.
    Stamps every chunk with rigorous provenance metadata.
    """
    chunks = []
    
    for page_data in pages:
        source = page_data["source"]
        page_num = page_data["page"]
        text = page_data["text"]
        
        text_length = len(text)
        chunk_index = 0
        i = 0
        
        # Slide our window across the page text
        while i < text_length:
            # Calculate where this chunk should end
            end = min(i + chunk_size, text_length)
            chunk_text = text[i:end]
            
            # Create a unique, traceable ID for this chunk
            chunk_id = f"{source}_p{page_num}_c{chunk_index}"
            
            # Append the heavily-tracked chunk object
            chunks.append({
                "chunk_id": chunk_id,
                "source": source,
                "page": page_num,
                "char_start": i,
                "char_end": end,
                "text": chunk_text
            })
            
            chunk_index += 1
            
            # Move our pointer forward, but step back by the overlap
            # Ensure we always move forward at least 1 character to prevent infinite loops
            step = max(1, chunk_size - overlap)
            i += step
            
    return chunks

if __name__ == "__main__":
    # Point directly to our sample.txt file we created in Pack 1
    target_file = os.path.join(current_dir, "sample.txt")
    
    print("=== CHUNKING DOCUMENT ===")
    
    # 1. Ingest the document (reusing Pack 1's code!)
    ingested_pages = ingest_document(target_file)
    
    if not ingested_pages:
        print("Failed to ingest document. Ensure sample.txt exists.")
        sys.exit(1)
        
    # 2. Chunk the document
    production_chunks = chunk_document(ingested_pages, chunk_size=400, overlap=80)
    
    # 3. Print the results to verify metadata
    for c in production_chunks:
        # Clean up newlines for a neat console preview
        clean_text = c['text'][:80].replace('\n', ' ')
        print(f"Chunk {c['chunk_id']} | chars {c['char_start']}-{c['char_end']} | {clean_text}...")
        
    print(f"\nTotal chunks produced: {len(production_chunks)}")