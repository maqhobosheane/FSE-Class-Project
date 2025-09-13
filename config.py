import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration from environment variables."""
    SECRET_KEY = os.getenv('SECRET_KEY')
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
    DATABASE_URL = os.getenv('DATABASE_URL')
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    WEBHOOK_URL = os.getenv('WEBHOOK_URL')

    # Basic validation
    if not all([TELEGRAM_BOT_TOKEN, WEBHOOK_URL, DATABASE_URL, ENCRYPTION_KEY]):
        raise ValueError("One or more critical environment variables are not set.")

config = Config()