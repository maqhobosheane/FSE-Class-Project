#!/usr/bin/env python3
"""
Update schema using the same configuration as the running app
"""
import os
import sys

# Add the current directory to path
sys.path.append('.')

# Load environment variables the same way your app does
from dotenv import load_dotenv
load_dotenv()

# Use the DATABASE_URL from your .env file
DATABASE_URL = os.getenv('DATABASE_URL')
print(f"Using DATABASE_URL: {DATABASE_URL}")

from sqlalchemy import create_engine
from app.database.models import Base

try:
    # Create engine directly from DATABASE_URL
    engine = create_engine(DATABASE_URL)
    
    print("Testing connection...")
    with engine.connect() as conn:
        print("✅ Connection successful!")
    
    print("Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("Creating new tables...")
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database schema updated successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")