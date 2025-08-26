import asyncio
import json
import os
import uuid
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
from ai_blog_app import generate_blog_post_with_review

# --- Initialization ---
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


async def summarize_table_with_llm(table_html: str) -> str:
    """
    Uses a generative LLM to create a natural language summary of an HTML table.
    """
    print("--- Generating summary for table... ---")
    prompt = (
        "You are a data analyst. Your task is to provide a concise, natural language summary "
        "of the following HTML table. Describe the main contents and purpose of the table.\n\n"
        f"TABLE:\n{table_html}"
    )
    summary = await generate_blog_post_with_review(
        topic=prompt, provider="openai", model="gpt-3.5-turbo", max_words=150
    )
    return summary

async def process_and_embed_document(json_filename: str, smart_indexing: bool = False):
    """
    Reads a processed JSON file, chunks, embeds, and uploads the data to Qdrant.
    If smart_indexing is True, it will also generate LLM summaries for tables.
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

    chunks_with_metadata = []
    current_section = "Introduction"

    for element in filtered_elements:
        element_text = element.get("text", "")
        element_type = element.get("type")

        # Update the current section if we find a title
        if element_type == "Title":
            current_section = element_text

        # Apply smart indexing for tables if the flag is set
        if element_type == "Table" and smart_indexing:
            print(f"--- Smart indexing enabled for table in section: {current_section} ---")
            # 1. Add the raw HTML
            chunks_with_metadata.append({
                "text": element_text,
                "metadata": {"source_file": json_filename, "section": current_section, "type": "table_html"}
            })
            # 2. Add the AI-generated summary
            summary = await summarize_table_with_llm(element_text)
            chunks_with_metadata.append({
                "text": summary,
                "metadata": {"source_file": json_filename, "section": current_section, "type": "table_summary"}
            })
        else:
            # For all other elements, or if smart_indexing is off, just add the text
            chunks_with_metadata.append({
                "text": element_text,
                "metadata": {"source_file": json_filename, "section": current_section, "type": element_type}
            })

    print(f"--- Created {len(chunks_with_metadata)} chunks to embed. ---")

    if not chunks_with_metadata:
        print("--- No chunks were created. Skipping embedding. ---")
        return

 # Prepare the payloads and texts for embedding
    payloads = []
    texts_to_embed = []
    for chunk in chunks_with_metadata:
        # The text to be embedded
        texts_to_embed.append(chunk["text"])
        payload = chunk["metadata"]
        payload["text"] = chunk["text"]
        payloads.append(payload)


    # Create embeddings and upload to Qdrant
    vectors = embedding_model.encode(texts_to_embed, show_progress_bar=True)
    qdrant_client.upsert(
        collection_name=collection_name,
        points=models.Batch(
            ids=[str(uuid.uuid4()) for _ in texts_to_embed],
            vectors=vectors,
            payloads=payloads
        )
    )
    print(f"--- Successfully uploaded {len(chunks_with_metadata)} chunks to Qdrant. ---")


# --- Testing Block ---
if __name__ == "__main__":
    # Make sure to delete your qdrant_storage folder and restart the container first!
    test_file = "20250825-160321_IZUMDINNER.json"
    
    # Set smart_indexing to True to generate summaries, or False for fast mode.
    asyncio.run(process_and_embed_document(test_file, smart_indexing=True))