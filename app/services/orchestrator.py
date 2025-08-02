import os
import io
import pymupdf  # For PDF generation
from dotenv import load_dotenv
from typing import Optional
from ai_blog_app import generate_blog_post_with_review

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
        context: Optional[str] = None
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
            context=context
        )
        print("\n--- Generation complete! ---")
        print(final_post)
    except Exception as e:
        print(f"--- ERROR during generation: {e} ---")