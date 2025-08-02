import os
from dotenv import load_dotenv
from ai_blog_app import generate_blog_post_with_review

# Load environment variables (e.g., GEMINI_API_KEY)
# This is a good place for it, as it's close to where the key is used.
load_dotenv() 

async def run_generation_workflow(topic: str, provider: str, model: str | None):
    """
    Runs the core blog generation logic from your library.
    NOTE: In a real app, you would save the 'final_post' to a database here.
    """
    print(f"\n--- Starting generation for topic: '{topic}' ---")
    try:
        final_post = await generate_blog_post_with_review(
            topic=topic,
            provider=provider,
            model=model
        )
        print("\n--- Generation complete! ---")
        print(final_post) # For now, we just print the result to the console
    except Exception as e:
        print(f"--- ERROR during generation: {e} ---")