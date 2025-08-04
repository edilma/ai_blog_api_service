from sqlmodel import Session
from app.db.models import BlogPost

def save_blog_post(topic: str, content: str, session: Session):
    """Creates a new BlogPost record and saves it to the database."""
    db_post = BlogPost(topic=topic, content=content)
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post