import telebot
from config import config

# Initialize Telegram bot
bot = telebot.TeleBot(config.TELEGRAM_BOT_TOKEN)
