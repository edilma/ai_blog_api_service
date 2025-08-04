from sqlmodel import Session,select
from app.db.models import BlogPost

def save_blog_post(topic: str, content: str, session: Session):
    """Creates a new BlogPost record and saves it to the database."""
    db_post = BlogPost(topic=topic, content=content)
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post

def get_blog_posts(session: Session) -> list[BlogPost]:
    """Fetches all blog post records from the database."""
    statement = select(BlogPost)
    results = session.exec(statement)
    return results.all()

def get_blog_post_by_id(post_id: int, session: Session) -> BlogPost | None:
    """Fetches a single blog post by its ID."""
    return session.get(BlogPost, post_id)
