from sqlalchemy import Column, Integer, String, BigInteger
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    wallet_address = Column(String, unique=True, nullable=False)
    encrypted_seed = Column(String, nullable=False) # Store encrypted seed

    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, wallet_address='{self.wallet_address}')>"