import telebot
from flask import request
from app.database.session import get_db
from app.telegram_bot import handlers
from app import flask_app
from app.bot import bot

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

# This is the main endpoint that Telegram will send updates to
@flask_app.route('/telegram-webhook', methods=['POST'])
def webhook():
    """Handles incoming updates from Telegram."""
    try:
        if request.headers.get('content-type') == 'application/json':
            json_string = request.get_data().decode('utf-8')
            print(f"DEBUG: Received webhook data: {json_string}")
            update = telebot.types.Update.de_json(json_string)
            print(f"DEBUG: Parsed update: {update}")
            print(f"DEBUG: About to process update with bot: {bot}")
            print(f"DEBUG: Bot handlers before processing: {len(bot.message_handlers)} message handlers, {len(bot.callback_query_handlers)} callback handlers")
            try:
                bot.process_new_updates([update])
                print("DEBUG: Successfully processed update")
            except Exception as e:
                print(f"DEBUG: Exception in bot.process_new_updates: {str(e)}")
                import traceback
                traceback.print_exc()
            return 'OK', 200
        else:
            print(f"DEBUG: Unsupported content type: {request.headers.get('content-type')}")
            return 'Unsupported Media Type', 415
    except Exception as e:
        print(f"DEBUG: Error in webhook handler: {str(e)}")
        import traceback
        traceback.print_exc()
        return 'Internal Server Error', 500

# --- Message and Callback Handlers ---

print(f"DEBUG: Registering handlers with bot: {bot}")

@bot.message_handler(commands=['start'])
def start_command_handler(message: telebot.types.Message):
    try:
        print(f"DEBUG: Start command received from user {message.from_user.id}")
        db = next(get_db())
        handlers.handle_start_command(bot, message, db)
        print("DEBUG: Start command processed successfully")
    except Exception as e:
        print(f"DEBUG: Error in start command handler: {str(e)}")
        import traceback
        traceback.print_exc()

@bot.message_handler(commands=['create'])
def create_command_handler(message: telebot.types.Message):
    try:
        print(f"DEBUG: Create command received from user {message.from_user.id}")
        # This handler is for users who type /create manually
        db = next(get_db())
        handlers.handle_create_command(bot, message, db)
        print("DEBUG: Create command processed successfully")
    except Exception as e:
        print(f"DEBUG: Error in create command handler: {str(e)}")
        import traceback
        traceback.print_exc()

@bot.callback_query_handler(func=lambda call: call.data == 'create_wallet')
def create_callback_handler(call: telebot.types.CallbackQuery):
    try:
        print(f"DEBUG: Callback query received from user {call.from_user.id}, data: {call.data}")
        # This handler is for the inline button press
        db = next(get_db())
        # Acknowledge the callback
        bot.answer_callback_query(call.id)
        # The message object within a callback is linked to the original message
        handlers.handle_create_command(bot, call.message, db)
        print("DEBUG: Callback query processed successfully")
    except Exception as e:
        print(f"DEBUG: Error in callback query handler: {str(e)}")
        import traceback
        traceback.print_exc()

# Debug: Print all registered handlers
print(f"DEBUG: All registered message handlers: {bot.message_handlers}")
print(f"DEBUG: All registered callback handlers: {bot.callback_query_handlers}")