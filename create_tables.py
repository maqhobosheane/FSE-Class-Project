print("Importing models...")

try:
    from app.database.models import Base
    from app.database.session import engine
    print(f"Database URL: {engine.url}")
    Base.metadata.create_all(bind=engine)
    print("The 'users' table has been created successfully!")
except Exception as e:
    print(f"Error creating tables: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)