from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import content
from app.db.database import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    This context manager handles application startup and shutdown events.
    """
    print("--- Application starting up... ---")
    create_db_and_tables()
    print("--- Database and tables verified. ---")
    yield
    print("--- Application shutting down... ---")

# Create the FastAPI app instance
app = FastAPI(
    title="AI Blog Generation API",
    description="An API for orchestrating AI agents to write blog posts.",
    version="2.0.0",
    lifespan=lifespan
)

# Include the router from our content.py file
app.include_router(content.router, prefix="/api", tags=["Content Generation"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the AI Blog Generation API!"}
