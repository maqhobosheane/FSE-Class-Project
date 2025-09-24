import pytest
from unittest.mock import Mock, patch
from io import BytesIO
from app.services import price_service
from app.database import crud

class TestPriceService:
    @patch('app.services.price_service.requests.get')
    def test_generate_price_chart_with_fresh_data(self, mock_get, db_session):
        """Test price service when no cache exists"""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "prices": [
                [1234567890000, 0.5],
                [1234567900000, 0.6]
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Mock the get_db function to return our test session
        with patch('app.services.price_service.get_db') as mock_get_db:
            mock_get_db.return_value = iter([db_session])
            
            # Call the function
            result = price_service.generate_price_chart_image()
            
            # Verify results
            assert isinstance(result, BytesIO)
            mock_get.assert_called_once()

    @patch('app.services.price_service.requests.get')
    def test_generate_price_chart_uses_cache(self, mock_get, db_session):
        """Test price service uses cached data when available"""
        # Create a cached entry first
        cached_data = {
            "prices": [
                [1234567890000, 0.5],
                [1234567900000, 0.6]
            ]
        }
        crud.save_price_cache(db_session, cached_data)
        
        # Mock the get_db function to return our test session
        with patch('app.services.price_service.get_db') as mock_get_db:
            mock_get_db.return_value = iter([db_session])
            
            # Call the function - should use cache, not call API
            result = price_service.generate_price_chart_image()
            
            # Verify API was NOT called (cache was used)
            mock_get.assert_not_called()
            assert isinstance(result, BytesIO)

    @patch('app.services.price_service.requests.get')
    def test_generate_price_chart_api_failure(self, mock_get, db_session):
        """Test price service handles API failures gracefully"""
        # Mock API failure
        mock_get.side_effect = Exception("API failure")
        
        # Mock the get_db function
        with patch('app.services.price_service.get_db') as mock_get_db:
            mock_get_db.return_value = iter([db_session])
            
            result = price_service.generate_price_chart_image()
            
            assert result is None

    def test_generate_price_chart_empty_data(self, db_session):
        """Test price service handles empty price data"""
        # Create cache with empty data
        crud.save_price_cache(db_session, {"prices": []})
        
        # Mock the get_db function
        with patch('app.services.price_service.get_db') as mock_get_db:
            mock_get_db.return_value = iter([db_session])
            
            result = price_service.generate_price_chart_image()
            
            assert result is None