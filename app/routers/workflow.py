import os
from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import List

# Import our indexing function
from app.services.indexing import process_and_embed_document

PROCESSED_DATA_DIR = "data/processed"

router = APIRouter()

@router.post("/index-document/{json_filename}")
async def index_document_endpoint(json_filename: str, background_tasks: BackgroundTasks):
    """
    Triggers the background task to index a specific processed document.
    """
    file_path = os.path.join(PROCESSED_DATA_DIR, json_filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Processed document not found.")

    # Run the full indexing pipeline as a background task
    background_tasks.add_task(
        process_and_embed_document,
        json_filename=json_filename,
        smart_indexing=True # Always use smart indexing for the main tool
    )
    return {"message": f"Indexing has started for {json_filename}. This may take a moment."}


@router.get("/processed-documents", response_model=List[str])
async def get_processed_documents():
    """
    Returns a list of all available documents that have been processed.
    """
    try:
        # Get all .json files from the directory and sort them by most recent
        files = [f for f in os.listdir(PROCESSED_DATA_DIR) if f.endswith('.json')]
        files.sort(key=lambda x: os.path.getmtime(os.path.join(PROCESSED_DATA_DIR, x)), reverse=True)
        return files
    except FileNotFoundError:
        return []