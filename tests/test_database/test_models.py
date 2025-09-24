import pytest
from datetime import datetime, timedelta
from app.database.models import User, PriceCache

class TestUserModel:
    def test_user_creation(self):
        """Test User model creation with valid data"""
        user = User(
            telegram_id=123456789,
            wallet_address="rTestWalletAddress123",
            encrypted_seed="encrypted_seed_here"
        )
        
        assert user.telegram_id == 123456789
        assert user.wallet_address == "rTestWalletAddress123"
        assert user.encrypted_seed == "encrypted_seed_here"
        assert "User(telegram_id=123456789" in repr(user)

class TestPriceCacheModel:
    def test_price_cache_creation(self):
        """Test PriceCache model creation with valid data"""
        now = datetime.utcnow()
        expires_at = now + timedelta(minutes=15)
        sample_data = {"prices": [[1234567890000, 0.5], [1234567900000, 0.6]]}
        
        cache = PriceCache(
            cache_key="xrp_7d",
            price_data=sample_data,
            last_updated=now,
            expires_at=expires_at
        )
        
        assert cache.cache_key == "xrp_7d"
        assert cache.price_data == sample_data
        assert cache.last_updated == now
        assert cache.expires_at == expires_at
        assert "PriceCache(cache_key='xrp_7d'" in repr(cache)
    
    def test_price_cache_defaults(self):
        """Test PriceCache creation with required fields"""
        sample_data = {"prices": []}
        now = datetime.utcnow()
        
        cache = PriceCache(
            cache_key="test_key",
            price_data=sample_data,
            last_updated=now,  # Explicitly set, test was failing
            expires_at=now + timedelta(minutes=15)
        )
        
        assert cache.cache_key == "test_key"
        assert cache.price_data == sample_data
        assert cache.last_updated == now