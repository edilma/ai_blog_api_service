from fastapi import APIRouter, BackgroundTasks

# Import our new model and service function
from app.models import BlogRequest
from app.services.orchestrator import run_generation_workflow

router = APIRouter()

@router.post("/generate-blog")
async def create_blog_post(request: BlogRequest, background_tasks: BackgroundTasks):
    """
    This endpoint accepts a blog post request and starts the generation
    process in the background.
    """
    background_tasks.add_task(
        run_generation_workflow,
        topic=request.topic,
        provider=request.provider,
        model=request.model
    )
    
    return {"message": "Blog post generation started in the background."}