import os
import io
import re
import pymupdf  # For PDF generation
from dotenv import load_dotenv
from typing import Optional
from sqlmodel import Session
import traceback

from ai_blog_app import generate_blog_post_with_review
from app.db.database import engine
from app.db.crud import save_blog_post

# Load environment variables (e.g., GEMINI_API_KEY)
load_dotenv() 

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extracts text from a PDF provided as bytes."""
    try:
        with pymupdf.open(stream=pdf_bytes, filetype="pdf") as pdf_document:
            full_text = [page.get_text() for page in pdf_document]
            return "\n".join(full_text)
    except Exception as e:
        print(f"--- ERROR extracting PDF text: {e} ---")
        return ""




async def run_generation_workflow(
        topic: str, 
        provider: str, 
        model: Optional[str], 
        context: Optional[str] = None,
        max_words: int = 300
    ):
    """
    Runs the core blog generation logic , now with optional context.
    """
    print(f"\n--- Starting generation for topic: '{topic}' ---")
    if context:
        print("--- Using context from uploaded PDF ---")


    try:
        final_post = await generate_blog_post_with_review(
            topic=topic,
            provider=provider,
            model=model,
            context=context,
            max_words=max_words
        )

        print("\n--- Generation complete! Saving to the database ---")
        # Save the final blog post to the database
        if not final_post:
            print("--- No blog post content generated. Skipping database save. ---")
            return
        
        with Session(engine) as session:
            saved_post = save_blog_post(
                topic=topic, 
                content=final_post, 
                session=session
            )
            print(f"--- Blog post saved with ID: {saved_post.id} ---")
        
    except Exception as e:
        print(f"--- AN EXCEPTION OCCURRED ---")
        # This will print the full, detailed error traceback
        traceback.print_exc()
    # ----------------------------------------------------