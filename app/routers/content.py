from fastapi import APIRouter, BackgroundTasks, UploadFile, File, Form
from typing import Optional, Annotated

# Import our service functions
from app.services.orchestrator import run_generation_workflow, extract_text_from_pdf

router = APIRouter()

@router.post("/generate-blog")
async def create_blog_post(
    background_tasks: BackgroundTasks,
    topic: Annotated[str, Form()],
    # --- This line has been corrected ---
    provider: Annotated[str, Form()] = "openai",
    # -----------------------------------
    model: Annotated[Optional[str], Form()] = None,
    pdf_file: Annotated[Optional[UploadFile], File()] = None
):
    """
    This endpoint accepts blog post details and an optional PDF file.
    It starts the generation process in the background.
    """
    context_text = None
    if pdf_file:
        # Read the file and extract text if it exists
        pdf_bytes = await pdf_file.read()
        context_text = extract_text_from_pdf(pdf_bytes)

    background_tasks.add_task(
        run_generation_workflow,
        topic=topic,
        provider=provider,
        model=model,
        context=context_text # Pass the extracted text or None
    )
    
    return {"message": "Blog post generation started in the background. If a PDF was provided, it will be used as context."}