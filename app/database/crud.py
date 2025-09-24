from sqlalchemy.orm import Session
from . import models
from datetime import datetime, timedelta

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

# New price cache CRUD operations
def get_price_cache(db: Session, cache_key: str = "xrp_7d"):
    """
    Get cached price data if it's still fresh (less than 15 minutes old)
    """
    fifteen_minutes_ago = datetime.utcnow() - timedelta(minutes=15)
    
    cache = db.query(models.PriceCache).filter(
        models.PriceCache.cache_key == cache_key,
        models.PriceCache.expires_at > datetime.utcnow()
    ).first()
    
    return cache

def save_price_cache(db: Session, price_data: dict, cache_key: str = "xrp_7d"):
    """
    Save or update price cache with 15-minute expiration
    """
    # Check if cache already exists
    existing_cache = db.query(models.PriceCache).filter(
        models.PriceCache.cache_key == cache_key
    ).first()
    
    expires_at = datetime.utcnow() + timedelta(minutes=15)
    
    if existing_cache:
        # Update existing cache
        existing_cache.price_data = price_data
        existing_cache.last_updated = datetime.utcnow()
        existing_cache.expires_at = expires_at
    else:
        # Create new cache
        existing_cache = models.PriceCache(
            cache_key=cache_key,
            price_data=price_data,
            last_updated=datetime.utcnow(),
            expires_at=expires_at
        )
        db.add(existing_cache)
    
    db.commit()
    db.refresh(existing_cache)
    return existing_cache