# app/database/session.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import config

# Create the database engine from the URL in the config
engine = create_engine(config.DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Provides a database session for a single request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()