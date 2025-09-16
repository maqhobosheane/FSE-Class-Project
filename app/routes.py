# app/routes.py
import telebot
from flask import request
from app import flask_app, bot
from app.database.session import get_db
from app.telegram_bot import handlers

@flask_app.route('/')
def index():
    return "Bot is running!", 200

@flask_app.route('/set_webhook')
def set_webhook():
    """A simple route to set the webhook (run once)."""
    webhook_url = f"{flask_app.config['WEBHOOK_URL']}/telegram-webhook"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    return f"Webhook set to {webhook_url}", 200

@flask_app.route('/telegram-webhook', methods=['POST'])
def webhook():
    """Handles incoming updates from Telegram."""
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    else:
        return 'Unsupported Media Type', 415

# --- Message and Callback Handlers ---

@bot.message_handler(commands=['start'])
def start_command_handler(message: telebot.types.Message):
    db = next(get_db())
    handlers.handle_start_command(bot, message, db)

@bot.message_handler(commands=['create'])
def create_command_handler(message: telebot.types.Message):
    db = next(get_db())
    handlers.handle_create_command(bot, message, db)

@bot.callback_query_handler(func=lambda call: call.data == 'create_wallet')
def create_callback_handler(call: telebot.types.CallbackQuery):
    db = next(get_db())
    bot.answer_callback_query(call.id)
    handlers.handle_create_command(bot, call.message, db)

# --- Placeholder Handlers for New Menu Buttons ---

@bot.callback_query_handler(func=lambda call: call.data == 'learn_more')
def learn_more_handler(call: telebot.types.CallbackQuery):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "This bot helps you manage an XRPL testnet wallet. (Functionality coming soon!)")

@bot.callback_query_handler(func=lambda call: call.data == 'check_balance')
def check_balance_handler(call: telebot.types.CallbackQuery):
    """Handles the 'check_balance' button, calling the new logic handler."""
    db = next(get_db())
    bot.answer_callback_query(call.id)
    # Call the new handler function with the business logic
    handlers.handle_check_balance(bot, call.message, db)

@bot.callback_query_handler(func=lambda call: call.data == 'send_xrp')
def send_xrp_handler(call: telebot.types.CallbackQuery):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "Let's send some XRP! (Functionality coming soon!)")
    
@bot.callback_query_handler(func=lambda call: call.data == 'view_price_history')
def price_history_handler(call: telebot.types.CallbackQuery):
    """Handles the 'view_price_history' button, calling the new logic handler."""
    db = next(get_db())
    bot.answer_callback_query(call.id)
    # Call the new handler function with the business logic
    handlers.handle_view_price_history(bot, call.message, db)