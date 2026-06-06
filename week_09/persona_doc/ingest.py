import os
from pypdf import PdfReader

def ingest_document(filepath: str) -> list[dict]:
    """
    Reads a document (.txt or .pdf) and returns a list of dictionaries.
    Each dictionary represents one page with metadata and text.
    """
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.")
        return []

    filename = os.path.basename(filepath)
    # Extract the file extension to determine how to parse it
    ext = os.path.splitext(filename)[1].lower()
    pages_data = []

    if ext == '.txt':
        # Handle simple text files (considered as 1 page)
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read().strip()
            pages_data.append({
                "source": filename,
                "page": 1,
                "text": text
            })
            
    elif ext == '.pdf':
        # Handle PDF files, iterating page by page
        try:
            reader = PdfReader(filepath)
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    pages_data.append({
                        "source": filename,
                        "page": i + 1,  # Page numbers should be 1-indexed for humans
                        "text": text.strip()
                    })
        except Exception as e:
            print(f"Error reading PDF: {e}")
            
    else:
        # Failsafe for unsupported formats
        print(f"Error: Unsupported file type '{ext}'")
        return []

    return pages_data

if __name__ == "__main__":
    # Test the ingestion on our sample file
    # Note: If running from the root directory, we need the correct path
    target_file = "week_09/persona_doc/sample.txt"
    filename_only = os.path.basename(target_file)
    
    print(f"=== INGESTING: {filename_only} ===")
    
    ingested_pages = ingest_document(target_file)
    
    for doc in ingested_pages:
        # Clean up newlines for a neat console preview
        clean_preview = doc['text'][:100].replace('\n', ' ')
        print(f"Page {doc['page']} | Source: {doc['source']} | Preview: {clean_preview}...")
        
    print(f"Total pages ingested: {len(ingested_pages)}")