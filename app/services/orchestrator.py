import os
from typing import Optional, List
from dotenv import load_dotenv
from sqlmodel import Session
from qdrant_client import models

# Import our clients and models from the indexing service
from .indexing import qdrant_client, embedding_model

from ai_blog_app import generate_blog_post_with_review
from app.db.database import engine
from app.db.crud import save_blog_post

load_dotenv()

async def run_generation_workflow(
    topic: str,
    provider: str,
    model: Optional[str],
    max_words: int,
    source_filenames: Optional[List[str]] = None 
):
    """
    Retrieves context from Qdrant based on the topic and source files,
    then generates and saves a blog post.
    """
    print(f"\n--- Starting generation for topic: '{topic}' ---")
    
    # --- 1. Create Query Embedding ---
    query_vector = embedding_model.encode(topic).tolist()

    # --- 2. Build Metadata Filter ---
    query_filter = None
    if source_filenames:
        print(f"--- Filtering context by source files: {source_filenames} ---")
        
        # Create a more flexible filter that checks multiple fields
        # This handles cases where filenames might be stored slightly differently
        # Use a simpler filter approach - direct match on source_file
        query_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="source_file",
                    match=models.MatchAny(any=source_filenames),
                )
            ]
        )

    # --- 3. Search Qdrant (Retrieve) ---
    search_limit = 10  # Increase limit to get more context
    
    try:
        # First try with filter if provided
        search_results = qdrant_client.search(
            collection_name="document_chunks",
            query_vector=query_vector,
            query_filter=query_filter,
            limit=search_limit
        )
        
        # If no results with filter, try without filter as fallback
        if not search_results and query_filter:
            print("--- No results with filter, trying without filter... ---")
            search_results = qdrant_client.search(
                collection_name="document_chunks",
                query_vector=query_vector,
                limit=search_limit
            )
    except Exception as e:
        print(f"--- ERROR during vector search: {repr(e)} ---")
        search_results = []
    
    # --- 4. Analyze & Log Results ---
    if search_results:
        print(f"--- Retrieved {len(search_results)} relevant chunks ---")
        for i, result in enumerate(search_results):
            source = result.payload.get("source_file", "unknown")
            doc_type = result.payload.get("type", "unknown")
            score = result.score
            print(f"  {i+1}. Score: {score:.4f} | Source: {source} | Type: {doc_type}")
    
    # --- 5. Construct Context ---
    context_chunks = []
    for result in search_results:
        # Add metadata context to each chunk
        chunk_text = result.payload.get("text", "")
        source = result.payload.get("source_file", "Unknown Source")
        section = result.payload.get("section", "Unknown Section")
        chunk_type = result.payload.get("type", "Unknown Type")
        
        # Format the chunk with metadata
        formatted_chunk = f"[SOURCE: {source} | SECTION: {section} | TYPE: {chunk_type}]\n{chunk_text}"
        context_chunks.append(formatted_chunk)
    
    # Join all chunks with separators
    context = "\n\n---\n\n".join(context_chunks)
    
    if not context:
        print("--- WARNING: No relevant context found in the vector database. ---")

    try:
        # --- 5. Generate and Save ---
        final_post = await generate_blog_post_with_review(
            topic=topic,
            provider=provider,
            model=model,
            max_words=max_words,
            context=context
        )
        
        if not final_post:
            print("--- No blog post content generated. Skipping database save. ---")
            return

        with Session(engine) as session:
            save_blog_post(topic=topic, content=final_post, session=session)
        
        print("--- Blog post generated and saved successfully! ---")

    except Exception as e:
        print(f"--- ERROR during generation: {repr(e)} ---")


        