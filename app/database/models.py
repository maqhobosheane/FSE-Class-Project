from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Text, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime  

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    wallet_address = Column(String, unique=True, nullable=False)
    encrypted_seed = Column(String, nullable=False) # Store encrypted seed

    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, wallet_address='{self.wallet_address}')>"

class PriceCache(Base):
    __tablename__ = "price_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String, unique=True, nullable=False, index=True)  
    price_data = Column(JSON, nullable=False)  # Store the full API response
    last_updated = Column(DateTime, default=datetime.utcnow, nullable=False)  # Add default 
    expires_at = Column(DateTime, nullable=False)  # When this cache should be considered stale
    
    def __repr__(self):
        return f"<PriceCache(cache_key='{self.cache_key}', last_updated={self.last_updated})>"