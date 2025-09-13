from sqlalchemy.orm import Session
from . import models

def get_user_by_telegram_id(db: Session, tg_id: int):
    """
    Checks if a user exists based on their Telegram ID.
    Corresponds to: check_user_exists(tg_id)
    """
    return db.query(models.User).filter(models.User.telegram_id == tg_id).first()

def save_new_user(db: Session, tg_id: int, address: str, encrypted_seed: str):
    """
    Saves a new user to the database.
    Corresponds to: save_new_user(...)
    """
    db_user = models.User(
        telegram_id=tg_id,
        wallet_address=address,
        encrypted_seed=encrypted_seed
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # Corresponds to: return confirm_new_user
    return db_user