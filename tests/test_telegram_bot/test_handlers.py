import pytest
from unittest.mock import Mock, patch
from app.telegram_bot import handlers
from app.database.models import User

class TestTelegramHandlers:
    def test_handle_view_price_history_with_user(self, db_session, mock_telebot):
        """Test price history handler when user exists"""
        # Create a test user
        user = User(
            telegram_id=123456789,
            wallet_address="rTestAddress123",
            encrypted_seed="encrypted_seed_here"
        )
        db_session.add(user)
        db_session.commit()
        
        # Mock the bot and message
        mock_bot = Mock()
        mock_chat_id = 123
        
        # Mock the price service to return a valid image
        with patch('app.telegram_bot.handlers.price_service.generate_price_chart_image') as mock_price_service:
            mock_price_service.return_value = Mock()  # Mock BytesIO object
            
            # Call the handler
            handlers.handle_view_price_history(mock_bot, mock_chat_id, 123456789, db_session)
            
            # Verify the bot sent the photo
            mock_bot.send_photo.assert_called_once()
            mock_price_service.assert_called_once()

    def test_handle_view_price_history_no_user(self, db_session, mock_telebot):
        """Test price history handler when user doesn't exist"""
        mock_bot = Mock()
        mock_chat_id = 123
        
        # Call the handler with non-existent user
        handlers.handle_view_price_history(mock_bot, mock_chat_id, 999999999, db_session)
        
        # Verify the bot sent the error message
        mock_bot.send_message.assert_called_with(mock_chat_id, "Please use /start and create a wallet first.")

    def test_handle_view_price_history_service_failure(self, db_session, mock_telebot):
        """Test price history handler when price service fails"""
        # Create a test user
        user = User(
            telegram_id=123456789,
            wallet_address="rTestAddress123",
            encrypted_seed="encrypted_seed_here"
        )
        db_session.add(user)
        db_session.commit()
        
        mock_bot = Mock()
        mock_chat_id = 123
        
        # Mock the price service to return None (failure)
        with patch('app.telegram_bot.handlers.price_service.generate_price_chart_image') as mock_price_service:
            mock_price_service.return_value = None
            
            # Call the handler
            handlers.handle_view_price_history(mock_bot, mock_chat_id, 123456789, db_session)
            
            # Verify the bot sent the error message
            mock_bot.send_message.assert_called_with(mock_chat_id, "Sorry, I couldn't generate the price chart at this time. Please try again later.")