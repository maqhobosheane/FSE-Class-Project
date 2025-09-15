from app.database.session import engine
from app.database.models import Base

def initialize_database():
    """Connects to the database and creates all tables."""
    print("Connecting to the database...")
    print("Creating database tables based on models...")
    
    # This command creates the tables
    Base.metadata.create_all(bind=engine)
    
    print("Tables created successfully! ✅")

if __name__ == "__main__":
    initialize_database()