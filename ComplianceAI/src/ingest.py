import os
import fitz  # PyMuPDF
import charset_normalizer
import logging

logger = logging.getLogger(__name__)


def ingest_document(filepath: str) -> list[dict]:
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
                    pages_data.append({"source": filename, "page": 1, "text": text})
        except Exception as e:
            logger.error(f"Error reading TXT/MD file: {e}")
    elif ext == '.pdf':
        try:
            doc = fitz.open(filepath)
            if doc.needs_pass:
                logger.error(f"PDF '{filename}' is password protected.")
                return []
            for i, page in enumerate(doc):
                text = page.get_text()
                if text and text.strip():
                    pages_data.append({"source": filename, "page": i + 1, "text": text.strip()})
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
    else:
        logger.error(f"Unsupported file type '{ext}'")
        return []
    return pages_data
