import pytest
from datetime import datetime, timedelta
from app.database import crud
from app.database.models import User, PriceCache

class TestUserCRUD:
    def test_get_user_by_telegram_id(self, db_session):
        """Test retrieving user by Telegram ID"""
        # Create a test user
        user = User(
            telegram_id=987654321,
            wallet_address="rTestAddress987",
            encrypted_seed="encrypted_test_seed"
        )
        db_session.add(user)
        db_session.commit()
        
        # Test retrieval
        found_user = crud.get_user_by_telegram_id(db_session, 987654321)
        assert found_user is not None
        assert found_user.telegram_id == 987654321
        assert found_user.wallet_address == "rTestAddress987"
    
    def test_get_nonexistent_user(self, db_session):
        """Test retrieving a user that doesn't exist"""
        found_user = crud.get_user_by_telegram_id(db_session, 999999999)
        assert found_user is None
    
    def test_save_new_user(self, db_session):
        """Test saving a new user"""
        user = crud.save_new_user(
            db_session, 
            tg_id=111222333, 
            address="rNewUserAddress", 
            encrypted_seed="new_encrypted_seed"
        )
        
        assert user.id is not None
        assert user.telegram_id == 111222333
        assert user.wallet_address == "rNewUserAddress"

class TestPriceCacheCRUD:
    def test_save_and_retrieve_price_cache(self, db_session):
        """Test saving and retrieving price cache"""
        sample_data = {"prices": [[1234567890000, 0.5], [1234567900000, 0.6]]}
        
        # Save cache
        cache = crud.save_price_cache(db_session, sample_data)
        assert cache.id is not None
        assert cache.cache_key == "xrp_7d"
        assert cache.price_data == sample_data
        
        # Retrieve cache
        retrieved_cache = crud.get_price_cache(db_session)
        assert retrieved_cache is not None
        assert retrieved_cache.price_data == sample_data
    
    def test_get_fresh_cache(self, db_session):
        """Test retrieving fresh cache (not expired)"""
        sample_data = {"prices": [[1234567890000, 0.5]]}
        future_time = datetime.utcnow() + timedelta(hours=1)
        
        cache = PriceCache(
            cache_key="xrp_7d",
            price_data=sample_data,
            last_updated=datetime.utcnow(),
            expires_at=future_time
        )
        db_session.add(cache)
        db_session.commit()
        
        retrieved_cache = crud.get_price_cache(db_session)
        assert retrieved_cache is not None
        assert retrieved_cache.expires_at > datetime.utcnow()
    
    def test_get_stale_cache_returns_none(self, db_session):
        """Test that stale cache is not returned"""
        sample_data = {"prices": [[1234567890000, 0.5]]}
        past_time = datetime.utcnow() - timedelta(minutes=1)
        
        cache = PriceCache(
            cache_key="xrp_7d",
            price_data=sample_data,
            last_updated=past_time,
            expires_at=past_time
        )
        db_session.add(cache)
        db_session.commit()
        
        retrieved_cache = crud.get_price_cache(db_session)
        assert retrieved_cache is None
    
    def test_update_existing_cache(self, db_session):
        """Test updating existing cache data"""
        # Create initial cache
        initial_data = {"prices": [[1, 0.5]]}
        cache = crud.save_price_cache(db_session, initial_data)
        original_id = cache.id
        original_timestamp = cache.last_updated
        
        # Update cache
        updated_data = {"prices": [[2, 0.6]]}
        updated_cache = crud.save_price_cache(db_session, updated_data)
        
        # Verify it's the same record (same ID) with updated data
        assert updated_cache.id == original_id
        assert updated_cache.price_data == updated_data
        
        # Robust timestamp check: should be the same or newer
        # Using >= handles the case where update happens in the same microsecond
        assert updated_cache.last_updated >= original_timestamp
        
        # Additional check: if timestamps are equal, verify the data actually changed
        if updated_cache.last_updated == original_timestamp:
            assert updated_cache.price_data != cache.price_data
            print("⚠️  Timestamps are identical but data was updated (microsecond precision)")
        else:
            assert updated_cache.last_updated > original_timestamp