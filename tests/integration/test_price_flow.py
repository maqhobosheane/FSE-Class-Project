import pytest
from unittest.mock import patch, Mock
from datetime import datetime, timedelta
from app.database import crud
from app.services import price_service

class TestPriceFlowIntegration:
    def test_complete_price_flow(self, db_session):
        """Integration test: complete flow from cache check to chart generation"""
        # Initially, no cache should exist
        initial_cache = crud.get_price_cache(db_session)
        assert initial_cache is None
        
        # Mock API call for fresh data
        with patch('app.services.price_service.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "prices": [
                    [1234567890000, 0.5],
                    [1234567900000, 0.6],
                    [1234567910000, 0.7]
                ]
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            with patch('app.services.price_service.get_db') as mock_get_db:
                mock_get_db.return_value = iter([db_session])
                
                # First call - should fetch from API and cache
                result1 = price_service.generate_price_chart_image()
                assert result1 is not None
                
                # Verify cache was created
                cache_after_first_call = crud.get_price_cache(db_session)
                assert cache_after_first_call is not None
                assert len(cache_after_first_call.price_data['prices']) == 3
        
        # Second call - should use cache (no API call)
        with patch('app.services.price_service.requests.get') as mock_get:
            with patch('app.services.price_service.get_db') as mock_get_db:
                mock_get_db.return_value = iter([db_session])
                
                result2 = price_service.generate_price_chart_image()
                assert result2 is not None
                
                # API should NOT be called this time
                mock_get.assert_not_called()