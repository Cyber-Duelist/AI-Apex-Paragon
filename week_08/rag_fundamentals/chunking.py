# 1. Our long document (Simulated Merger Agreement)
document = (
    "This merger agreement outlines the definitive terms under which Company A will acquire Company B. "
    "It was officially signed and executed on January 10, 2024. "
    "Both parties agree to the financial terms and regulatory stipulations detailed herein. "
    "The agreement covers all current subsidiaries and intellectual property owned by Company B. "
    "Upon completion, Company B will operate as a wholly-owned subsidiary of Company A. "
    "The board of directors for both organizations unanimously approved this transaction. "
    "Shareholders of Company B will receive a 15 percent premium on their current stock valuation. "
    "Legal compliance teams have initiated the antitrust review process with federal regulators. "
    "The target closing date for the acquisition is set for the third quarter of this fiscal year. "
    "Any disputes arising from this document will be settled through binding arbitration in Delaware. "
    "This document supersedes any prior communications or letters of intent between the parties. "
    "We anticipate a smooth transition for all employees and executives involved."
)

print("=== STRATEGY 1: FIXED SIZE CHUNKS (size=200, overlap=50) ===")
# Strategy 1: Fixed Size Chunking
# Splits exactly by character count. Good for uniform data, but might cut words in half.
# The 'overlap' ensures we don't accidentally split a key concept down the middle.
chunk_size = 200
overlap = 50
fixed_chunks = []

# Move through the document, sliding our 'window' by (chunk_size - overlap)
i = 0
while i < len(document):
    chunk = document[i:i + chunk_size]
    fixed_chunks.append(chunk)
    # Move forward, but step back by the overlap amount
    i += (chunk_size - overlap)

for idx, chunk in enumerate(fixed_chunks, 1):
    # Replace newlines for cleaner console printing
    clean_chunk = chunk.replace('\n', ' ').strip()
    print(f"Chunk {idx} ({len(clean_chunk)} chars): {clean_chunk}...")

print(f"\nTotal chunks: {len(fixed_chunks)}\n")

print("=== STRATEGY 2: SENTENCE CHUNKS (2 sentences per chunk) ===")
# Strategy 2: Sentence Chunking
# Splits by grammatical boundaries (like periods). Keeps complete thoughts together.
# Much better for LLMs reading the text later.

# Split by period, clean up whitespace, and add the period back
raw_sentences = document.split('.')
sentences = [s.strip() + "." for s in raw_sentences if s.strip()]

sentence_chunks = []
sentences_per_chunk = 2

# Step through the list of sentences 2 at a time
for i in range(0, len(sentences), sentences_per_chunk):
    # Grab a slice of up to 2 sentences and join them with a space
    group = sentences[i:i + sentences_per_chunk]
    chunk = " ".join(group)
    sentence_chunks.append((chunk, len(group)))

for idx, (chunk, count) in enumerate(sentence_chunks, 1):
    print(f"Chunk {idx} ({count} sentences): {chunk}")

print(f"\nTotal chunks: {len(sentence_chunks)}")