#!/usr/bin/env python3
"""
Simple working Telegram bot - bypasses all complex issues
"""
import os
import telebot
from flask import Flask, request

# Get bot token from environment
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not BOT_TOKEN:
    print("ERROR: TELEGRAM_BOT_TOKEN not set!")
    exit(1)

# Initialize bot and Flask
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Simple handler
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "Hello! I'm working! 🎉")

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    bot.reply_to(message, f"You said: {message.text}")

# Webhook endpoint
@app.route('/telegram-webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Bad Request', 400

@app.route('/')
def index():
    return "Simple bot is running!", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
