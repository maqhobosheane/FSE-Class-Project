#!/usr/bin/env python3
"""
Debug script to check database and Telegram ID issues
"""

from app.database.session import get_db
from app.database import crud, models
from sqlalchemy.orm import Session

def debug_database():
    """Debug the database to see what's stored"""
    print("=== DATABASE DEBUG ===")
    
    # Get a database session
    db = next(get_db())
    
    try:
        # Check all users in the database
        all_users = db.query(models.User).all()
        print(f"Total users in database: {len(all_users)}")
        
        for user in all_users:
            print(f"User ID: {user.id}")
            print(f"Telegram ID: {user.telegram_id} (type: {type(user.telegram_id)})")
            print(f"Wallet Address: {user.wallet_address}")
            print(f"Encrypted Seed: {user.encrypted_seed[:20]}...")
            print("---")
            
        # Test a specific lookup
        if all_users:
            test_tg_id = all_users[0].telegram_id
            print(f"\nTesting lookup for telegram_id: {test_tg_id}")
            found_user = crud.get_user_by_telegram_id(db, test_tg_id)
            print(f"Lookup result: {found_user}")
            
    except Exception as e:
        print(f"Error during database debug: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_database()
