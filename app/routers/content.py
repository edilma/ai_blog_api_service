from fastapi import APIRouter, BackgroundTasks, UploadFile, File, Form
from typing import Optional, Annotated
from sqlmodel import Session
from fastapi import Depends, HTTPException

from app.db.database import engine
from app.db import crud
from app.db.models import BlogPost 


# Import our service functions
from app.services.orchestrator import run_generation_workflow

router = APIRouter()

@router.post("/generate-blog")
async def create_blog_post(
    background_tasks: BackgroundTasks,
    topic: Annotated[str, Form()],
    provider: Annotated[str, Form()] = "openai",
    model: Annotated[Optional[str], Form()] = None,
    max_words: Annotated[int, Form()] = 300,
    # --- New parameter for source files ---
    source_files: Annotated[Optional[str], Form()] = None
):
    """
    Accepts a blog post topic and an optional, comma-separated list of
    source files to use for context.
    """
    # Convert the comma-separated string into a list
    source_filenames_list = None
    if source_files:
        source_filenames_list = [filename.strip() for filename in source_files.split(',')]

    background_tasks.add_task(
        run_generation_workflow,
        topic=topic,
        provider=provider,
        model=model,
        max_words=max_words,
        source_filenames=source_filenames_list # Pass the list to the workflow
    )
    
    return {"message": "Blog post generation with context has started."}


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