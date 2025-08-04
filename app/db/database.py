from sqlmodel import create_engine

# The database file will be named 'blog.db' in the root of your project
sqlite_file_name = "blog.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# The engine is the main connection to the database
# echo=True will print all the SQL statements it executes
engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    """Creates the database file and the BlogPost table if they don't exist."""
    # This imports the models so SQLModel knows what tables to create
    from app.db import models 
    models.SQLModel.metadata.create_all(engine)