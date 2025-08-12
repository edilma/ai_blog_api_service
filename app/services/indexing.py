import json
import os
import uuid
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

# --- (Initialization is the same) ---
qdrant_client = QdrantClient(host="localhost", port=6333)
embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
collection_name = "document_chunks"

try:
    qdrant_client.get_collection(collection_name=collection_name)
    print(f"Collection '{collection_name}' already exists.")
except Exception:
    print(f"Creating collection '{collection_name}' with Binary Quantization...")
    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=embedding_model.get_sentence_embedding_dimension(),
            distance=models.Distance.COSINE
        ),
        quantization_config=models.BinaryQuantization(
            binary=models.BinaryQuantizationConfig(always_ram=True)
        )
    )
    print(f"Collection '{collection_name}' created successfully.")


# --- NEW: Enhanced Chunking Function with Metadata ---
def chunk_by_title(elements: list, filename: str, max_characters: int = 1000) -> list[dict]:
    """
    Combines document elements into structured chunks with metadata, using titles as section breaks.
    """
    chunks = []
    current_chunk_text = ""
    current_section = "Introduction" # Default section if no title is found first

    for element in elements:
        element_text = element.get("text", "")
        element_type = element.get("type")

        if element_type == "Title":
            # If we have a pending chunk, save it before starting a new one
            if current_chunk_text.strip():
                chunks.append({
                    "text": current_chunk_text.strip(),
                    "metadata": {"source_file": filename, "section": current_section}
                })
            # The new section is the text of the title
            current_section = element_text
            current_chunk_text = element_text # The title starts the new chunk
        else:
            # If adding the next element would make the chunk too big, save the current one
            if len(current_chunk_text) + len(element_text) > max_characters:
                if current_chunk_text.strip():
                    chunks.append({
                        "text": current_chunk_text.strip(),
                        "metadata": {"source_file": filename, "section": current_section}
                    })
                current_chunk_text = element_text # Start a new chunk
            else:
                current_chunk_text += "\n" + element_text

    # Add the very last chunk
    if current_chunk_text.strip():
        chunks.append({
            "text": current_chunk_text.strip(),
            "metadata": {"source_file": filename, "section": current_section}
        })
        
    return chunks


# --- MODIFIED: Main Indexing Function ---
def process_and_embed_document(json_filename: str):
    """
    Reads a processed JSON file, filters, chunks with metadata, embeds, and uploads to Qdrant.
    """
    file_path = os.path.join("data/processed", json_filename)
    print(f"\n--- Starting indexing for: {file_path} ---")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            elements = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Processed file not found at '{file_path}'")
        return

    # Filter out noise
    filtered_elements = [
        el for el in elements 
        if el.get("type") not in ["Header", "Footer"] and el.get("text", "").strip()
    ]

    # Use our new, smarter chunking function
    structured_chunks = chunk_by_title(filtered_elements, filename=json_filename)

    print(f"--- Created {len(structured_chunks)} structured chunks to embed. ---")

    if not structured_chunks:
        print("--- No chunks were created. Skipping embedding. ---")
        return

    # Separate the text and metadata for processing
    texts_to_embed = [chunk["text"] for chunk in structured_chunks]
    metadata_payloads = [chunk["metadata"] for chunk in structured_chunks]

    # Create embeddings
    vectors = embedding_model.encode(texts_to_embed, show_progress_bar=True)

    # Upload to Qdrant with the rich metadata in the payload
    qdrant_client.upsert(
        collection_name=collection_name,
        points=models.Batch(
            ids=[str(uuid.uuid4()) for _ in texts_to_embed],
            vectors=vectors,
            payloads=metadata_payloads # <-- Use our new metadata payloads
        )
    )

    print(f"--- Successfully uploaded {len(structured_chunks)} chunks to Qdrant. ---")


# --- (The testing block remains the same) ---
if __name__ == "__main__":
    # Make sure to delete your qdrant_storage folder and restart the container first!
    #test_file = "20250811-110500_el_nino.json" 
    test_file = "20250812-073410_embed-tables-sample.json"

    process_and_embed_document(test_file)