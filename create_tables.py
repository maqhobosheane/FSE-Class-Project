print("Importing models...")

from app.database.models import Base
from app.database.session import engine

# Drop all tables first to clean up
Base.metadata.drop_all(bind=engine)

# Create all tables with the new schema
Base.metadata.create_all(bind=engine)

print("The 'users' and 'price_cache' tables have been recreated successfully!")
print("Note: This will delete all existing data. Use migrations in production.")