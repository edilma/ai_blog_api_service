import datetime
from datetime import UTC
from sqlmodel import Field, SQLModel

class BlogPost(SQLModel, table=True):
    """Defines the database table for storing blog posts."""
    id: int | None = Field(default=None, primary_key=True)
    topic: str
    content: str
    status: str = "completed"
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(UTC))