from fastapi import APIRouter, BackgroundTasks, UploadFile, File, Form
from typing import Optional, Annotated
from sqlmodel import Session
from fastapi import Depends, HTTPException

from app.db.database import engine
from app.db import crud
from app.db.models import BlogPost 


# Import our service functions
from app.services.orchestrator import run_generation_workflow, extract_text_from_pdf

router = APIRouter()

@router.post("/generate-blog")
async def create_blog_post(
    background_tasks: BackgroundTasks,
    topic: Annotated[str, Form()],
    provider: Annotated[str, Form()] = "openai",
    model: Annotated[Optional[str], Form()] = None,
    max_words: Annotated[int, Form()] = 300,
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
        context=context_text,
        max_words=max_words
    )
    
    return {"message": "Blog post generation started in the background. If a PDF was provided, it will be used as context."}

# This is a dependency that provides a database session to the endpoint
def get_session():
    with Session(engine) as session:
        yield session

@router.get("/posts", response_model=list[BlogPost])
def read_all_posts(session: Session = Depends(get_session)):
    """
    Retrieve all blog posts from the database.
    """
    db_posts = crud.get_blog_posts(session=session)
    return db_posts

@router.get("/posts/{post_id}", response_model=BlogPost)
def read_single_post(post_id: int, session: Session = Depends(get_session)):
    """
    Retrieve a single blog post by its ID.
    """
    db_post = crud.get_blog_post_by_id(post_id=post_id, session=session)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return db_post