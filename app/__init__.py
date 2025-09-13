import telebot
from flask import Flask
from config import config

# Initialize Flask app
flask_app = Flask(__name__)
flask_app.config.from_object(config)

# Initialize Telegram bot
bot = telebot.TeleBot(config.TELEGRAM_BOT_TOKEN)

# Import routes to register them with the app
from app import routes