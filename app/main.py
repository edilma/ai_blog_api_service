from fastapi import FastAPI
from app.routers import content

# Create the FastAPI app instance
app = FastAPI(
    title="AI Blog Generation API",
    description="An API for orchestrating AI agents to write blog posts.",
    version="1.0.0"
)

# Include the router from our content.py file
app.include_router(content.router, prefix="/api", tags=["Content Generation"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the AI Blog Generation API!"}