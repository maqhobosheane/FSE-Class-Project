print("Importing models...")

from app.database.models import Base
from app.database.session import engine
Base.metadata.create_all(bind=engine)

print("The 'users' table has been created successfully!")