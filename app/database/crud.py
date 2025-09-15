from sqlalchemy.orm import Session
from . import models

def get_user_by_telegram_id(db: Session, tg_id: int):
    """
    Checks if a user exists based on their Telegram ID.
    Corresponds to: check_user_exists(tg_id)
    """
    print(f"DEBUG CRUD: Looking up user with telegram_id: {tg_id} (type: {type(tg_id)})")
    result = db.query(models.User).filter(models.User.telegram_id == tg_id).first()
    print(f"DEBUG CRUD: Query result: {result}")
    return result

def save_new_user(db: Session, tg_id: int, address: str, encrypted_seed: str):
    """
    Saves a new user to the database.
    Corresponds to: save_new_user(...)
    """
    print(f"DEBUG CRUD SAVE: Saving user with telegram_id: {tg_id} (type: {type(tg_id)})")
    db_user = models.User(
        telegram_id=tg_id,
        wallet_address=address,
        encrypted_seed=encrypted_seed
    )
    print(f"DEBUG CRUD SAVE: Created user object: {db_user}")
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    print(f"DEBUG CRUD SAVE: Saved user with ID: {db_user.id}, telegram_id: {db_user.telegram_id}")
    # Corresponds to: return confirm_new_user
    return db_user