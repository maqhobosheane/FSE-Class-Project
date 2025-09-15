import sys
import os

# This is the crucial part that fixes the import error
# It tells the script where to find the 'app' folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import engine
from app.database.models import Base

def initialize_database():
    """Connects to the database and creates all tables."""
    print("Connecting to the database...")
    print("Creating database tables based on models...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully! ✅")

if __name__ == "__main__":
    initialize_database()