from pydantic import BaseModel
from typing import Optional

class BlogRequest(BaseModel):
    """Defines the request body for generating a blog post."""
    topic: str
    provider: str = "gemini"
    model: Optional[str] = "gemini-1.5-flash"