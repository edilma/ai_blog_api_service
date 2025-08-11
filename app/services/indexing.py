import json
import os
import uuid
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter

# --- 1. Initialize Clients and Models ---
# Connect to the Qdrant Docker container
qdrant_client = QdrantClient(host="localhost", port=6333)

# Load the embedding model (will download on first run)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# --- 2. Define Collection Configuration ---
collection_name = "document_chunks"

# Check if the collection exists and create it if it doesn't
try:
    qdrant_client.get_collection(collection_name=collection_name)
    print(f"Collection '{collection_name}' already exists.")
except Exception:
    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=embedding_model.get_sentence_embedding_dimension(), # 384 for MiniLM
            distance=models.Distance.COSINE
        )
    )
    print(f"Collection '{collection_name}' created successfully.")


# --- 3. The Main Indexing Function ---
def process_and_embed_document(json_filename: str):
    """
    Reads a processed JSON file, filters, chunks, embeds, and uploads the data to Qdrant.
    """
    file_path = os.path.join("data/processed", json_filename)
    print(f"\n--- Starting indexing for: {file_path} ---")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            elements = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Processed file not found at '{file_path}'")
        return

    # --- a. Filter Elements ---
    # We'll filter out common noise like headers and footers.
    filtered_elements = [
        el for el in elements 
        if el.get("type") not in ["Header", "Footer"]
    ]

    # --- b. Prepare Chunks ---
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    
    chunks_to_embed = []
    for element in filtered_elements:
        element_text = element.get("text", "")
        if element.get("type") == "Table":
            # For tables, treat the whole HTML as a single chunk
            chunks_to_embed.append(element_text)
        else:
            # For other text, use the splitter
            chunks_to_embed.extend(text_splitter.split_text(element_text))

    print(f"--- Created {len(chunks_to_embed)} chunks to embed. ---")

    # --- c. Create Embeddings and Upload to Qdrant ---
    # The model can process multiple chunks at once for efficiency
    vectors = embedding_model.encode(chunks_to_embed, show_progress_bar=True)

    # Upload the vectors and their corresponding text (payload) to Qdrant
    qdrant_client.upsert(
        collection_name=collection_name,
        points=models.Batch(
            ids=[str(uuid.uuid4()) for _ in chunks_to_embed], # Create a unique ID for each chunk
            vectors=vectors,
            payloads=[{"text": chunk} for chunk in chunks_to_embed] # Store the text with the vector
        )
    )

    print(f"--- Successfully uploaded {len(chunks_to_embed)} chunks to Qdrant. ---")