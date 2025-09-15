import telebot
from config import config

# Initialize Telegram bot
print(f"DEBUG: Initializing bot with token: {config.TELEGRAM_BOT_TOKEN[:10]}..." if config.TELEGRAM_BOT_TOKEN else "DEBUG: No bot token found!")
bot = telebot.TeleBot(config.TELEGRAM_BOT_TOKEN, threaded=False)
print(f"DEBUG: Bot initialized successfully: {bot}")
