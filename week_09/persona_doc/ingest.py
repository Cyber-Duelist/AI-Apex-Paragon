import os
import fitz  # PyMuPDF
import charset_normalizer
import csv
import logging

logger = logging.getLogger(__name__)

try:
    import docx
except ImportError:
    docx = None

def ingest_document(filepath: str) -> list[dict]:
    """
    Reads a document (.txt, .md, .csv, .docx, or .pdf) and returns a list of dictionaries.
    Each dictionary represents one page (or entire file) with metadata and text.
    """
    if not os.path.exists(filepath):
        logger.error(f"File '{filepath}' not found.")
        return []

    filename = os.path.basename(filepath)
    ext = os.path.splitext(filename)[1].lower()
    pages_data = []

    if ext in ['.txt', '.md']:
        try:
            with open(filepath, 'rb') as f:
                raw_data = f.read()
                result = charset_normalizer.detect(raw_data)
                encoding = result['encoding'] or 'utf-8'
                
                text = raw_data.decode(encoding, errors='replace').strip()
                if text:
                    pages_data.append({
                        "source": filename,
                        "page": 1,
                        "text": text
                    })
        except Exception as e:
            logger.error(f"Error reading TXT/MD file: {e}")
            
    elif ext == '.csv':
        try:
            with open(filepath, 'rb') as f:
                raw_data = f.read()
                result = charset_normalizer.detect(raw_data)
                encoding = result['encoding'] or 'utf-8'
                
                text_content = raw_data.decode(encoding, errors='replace')
                reader = csv.reader(text_content.splitlines())
                text = "\n".join([", ".join(row) for row in reader])
                if text.strip():
                    pages_data.append({
                        "source": filename,
                        "page": 1,
                        "text": text.strip()
                    })
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")

    elif ext == '.docx':
        if not docx:
            logger.error(f"python-docx not installed. Cannot process '{filename}'")
            return []
        try:
            doc = docx.Document(filepath)
            text = "\n".join([para.text for para in doc.paragraphs])
            if text.strip():
                pages_data.append({
                    "source": filename,
                    "page": 1,
                    "text": text.strip()
                })
        except Exception as e:
            logger.error(f"Error reading DOCX file: {e}")

    elif ext == '.pdf':
        try:
            doc = fitz.open(filepath)
            if doc.needs_pass:
                logger.error(f"PDF '{filename}' is password protected or encrypted.")
                return []
                
            for i, page in enumerate(doc):
                text = page.get_text()
                if text and text.strip():
                    pages_data.append({
                        "source": filename,
                        "page": i + 1,
                        "text": text.strip()
                    })
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
            
    else:
        logger.error(f"Unsupported file type '{ext}'")
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