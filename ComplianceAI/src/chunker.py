import os


def chunk_document(pages: list[dict], chunk_size: int = 400, overlap: int = 80) -> list[dict]:
    chunks = []
    for page_data in pages:
        source = page_data['source']
        page = page_data['page']
        text = page_data['text']
        start = 0
        index = 0
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end].strip()
            if chunk_text:
                base_name = os.path.splitext(source)[0]
                chunk_id = f"{base_name}_p{page}_c{index}"
                chunks.append({
                    'chunk_id': chunk_id,
                    'source': source,
                    'page': page,
                    'char_start': start,
                    'char_end': min(end, len(text)),
                    'text': chunk_text
                })
                index += 1
            start += chunk_size - overlap
    return chunks
