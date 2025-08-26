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
        query_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="source_file",
                    match=models.MatchAny(any=source_filenames),
                )
            ]
        )

    # --- 3. Search Qdrant (Retrieve) ---
    search_results = qdrant_client.search(
        collection_name="document_chunks",
        query_vector=query_vector,
        query_filter=query_filter,
        limit=5
    )
    
    # --- 4. Construct Context ---
    context = "\n\n---\n\n".join([result.payload["text"] for result in search_results])
    
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


        