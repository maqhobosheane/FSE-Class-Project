import telebot
from sqlalchemy.orm import Session
from app.database import crud
from app.services import price_service
from app.xrpl_client import wallet as xrpl_wallet
from xrpl.utils import drops_to_xrp
from app.utils.crypto import decrypt_seed, encrypt_seed
from . import keyboards

# --- Define a path for the welcome image ---
WELCOME_IMAGE_PATH = 'assets/welcome_xrp.jpg'

# --- Helper function to show the main menu ---
def _send_main_menu(bot: telebot.TeleBot, chat_id: int, text: str = "What would you like to do next?"):
    """Sends a message with the main menu keyboard attached."""
    bot.send_message(
        chat_id,
        text,
        reply_markup=keyboards.create_main_menu_keyboard()
    )

def handle_start_command(bot: telebot.TeleBot, message: telebot.types.Message, db: Session):
    """
    Handles the /start command.
    Now sends a photo and includes the user's balance on welcome back.
    """
    tg_id = message.from_user.id
    user = crud.get_user_by_telegram_id(db, tg_id=tg_id)

    try:
        with open(WELCOME_IMAGE_PATH, 'rb') as photo:
            if user:
                # --- Fetch balance and create a detailed welcome message ---
                bot.send_message(message.chat.id, "Fetching your details...")
                balance_in_drops = xrpl_wallet.get_account_balance(user.wallet_address)
                balance_str = "Could not fetch balance."
                if balance_in_drops is not None:
                    balance_in_xrp = drops_to_xrp(balance_in_drops)
                    balance_str = f"💰 Balance: *{balance_in_xrp:,.6f} XRP*"

                caption = (
                    f"Welcome back!\n\n"
                    f"📍 Address: `{user.wallet_address}`\n"
                    f"{balance_str}"
                )
                bot.send_photo(
                    message.chat.id,
                    photo=photo,
                    caption=caption,
                    parse_mode="Markdown",
                    reply_markup=keyboards.create_main_menu_keyboard()
                )
            else:
                # --- Send welcome image to new users ---
                caption = "Hello! 👋 It looks like you don't have an XRPL wallet with us yet. Click the button below to create one!"
                bot.send_photo(
                    message.chat.id,
                    photo=photo,
                    caption=caption,
                    reply_markup=keyboards.create_account_keyboard()
                )
    except FileNotFoundError:
        bot.send_message(message.chat.id, "Welcome! (Admin: Welcome image not found at assets/welcome_xrp.jpg)")
        if user:
            _send_main_menu(bot, message.chat.id, f"Welcome back!\nYour address is `{user.wallet_address}`")
        else:
             bot.send_message(message.chat.id, "Click the button below to create a wallet!", reply_markup=keyboards.create_account_keyboard())

def handle_learn_more(bot: telebot.TeleBot, chat_id: int):
    """
    Handles the 'Learn More' button click, providing info about the bot.
    """
    # --- Our documentation is attached ---
    google_doc_link = "https://1drv.ms/w/c/cf396881e1a7af9e/ERC20yu-Ch1Buw1PFjvBcNwBjQuzaq6-bkTvLbW6GEXzsA?e=wWAQxA" 

    learn_more_text = (
        "This bot allows you to store and send XRP to any of your peers on the XRPL testnet. 💸\n\n"
        "If you're nerdy like that and want to geek out on the architecture and systems design, you can find it all here:\n"
        f"[Project Documentation]({google_doc_link})\n\n"
        "But for now, here are the commands and what they do:\n\n"
        "➡️ *Check Balance* - See how much test XRP you've got.\n"
        "➡️ *View Price History* - Get a 7-day price chart for XRP in USD.\n"
        "➡️ *Send XRP* - Send some test XRP to another address.\n"
        "➡️ *Learn More* - That's this button right here! 😉"
    )

    bot.send_message(
        chat_id,
        learn_more_text,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )
    _send_main_menu(bot, chat_id)

def handle_create_command(bot: telebot.TeleBot, chat_id: int, tg_id: int, db: Session):
    """
    Handles the /create command or callback query.
    """
    if crud.get_user_by_telegram_id(db, tg_id=tg_id):
        bot.send_message(chat_id, "You already have a wallet! Here are your options:", reply_markup=keyboards.create_main_menu_keyboard())
        return

    bot.send_message(chat_id, "Generating your new XRPL wallet... 🛠️")
    
    new_wallet = xrpl_wallet.create_xrpl_account()
    if not new_wallet:
        bot.send_message(chat_id, "Sorry, there was an error creating your wallet. Please try again later.")
        _send_main_menu(bot, chat_id)
        return

    encrypted_seed = encrypt_seed(new_wallet.seed)
    crud.save_new_user(
        db=db, tg_id=tg_id, address=new_wallet.classic_address, encrypted_seed=encrypted_seed
    )

    response_text = (
        "🎉 Welcome! Your new XRPL wallet has been created and funded with test XRP.\n\n"
        f"*Address:* `{new_wallet.classic_address}`\n\n"
        "**IMPORTANT:** We have securely stored your encrypted seed. You are responsible for your account's security."
    )
    bot.send_message(
        chat_id, response_text, parse_mode="Markdown", reply_markup=keyboards.create_main_menu_keyboard()
    )


def handle_view_price_history(bot: telebot.TeleBot, chat_id: int, tg_id: int, db: Session):
    """
    Handles 'View Price History', generating and sending a chart.
    """
    user = crud.get_user_by_telegram_id(db, tg_id=tg_id)
    if not user:
        bot.send_message(chat_id, "Please use /start and create a wallet first.")
        return

    bot.send_message(chat_id, "Generating price chart... 📈")

    try:
        
        chart_image_buffer = price_service.generate_price_chart_image()
        
        if chart_image_buffer:
            caption = f"Here is the XRP price chart for the last 7 days.\n_Data from CoinGecko._"
            bot.send_photo(chat_id, photo=chart_image_buffer, caption=caption, parse_mode="Markdown")
        else:
            bot.send_message(chat_id, "Sorry, I couldn't generate the price chart at this time. Please try again later.")
    except Exception as e:
        print(f"!!!!!!!!!! ERROR in handle_view_price_history: {e} !!!!!!!!!!")
        bot.send_message(chat_id, "An unexpected error occurred while generating the chart. The developers have been notified.")
    finally:
        # --- Always show the main menu after an action ---
        _send_main_menu(bot, chat_id)


def handle_check_balance(bot: telebot.TeleBot, chat_id: int, tg_id: int, db: Session):
    """
    Handles the 'Check Balance' button click.
    """
    user = crud.get_user_by_telegram_id(db, tg_id=tg_id)
    if not user:
        bot.send_message(chat_id, "Please use /start and create a wallet first.")
        return

    balance_in_drops = xrpl_wallet.get_account_balance(user.wallet_address)
    
    if balance_in_drops is not None:
        balance_in_xrp = drops_to_xrp(balance_in_drops)
        response_text = f"💰 Your current balance is: *{balance_in_xrp:,.6f} XRP*"
    else:
        response_text = "Sorry, there was an error fetching your account balance."
        
    bot.send_message(chat_id, response_text, parse_mode="Markdown")
    _send_main_menu(bot, chat_id)


def handle_send_xrp(bot: telebot.TeleBot, chat_id: int, tg_id: int, db: Session):
    """
    Starts the send XRP process.
    """
    user = crud.get_user_by_telegram_id(db, tg_id=tg_id)
    if not user:
        bot.send_message(chat_id, "Please use /start and create a wallet first.")
        return
    
    msg = bot.send_message(chat_id, "Please reply with the destination XRPL address (r...). Or, click any menu button item below to cancel.")
    _send_main_menu(bot, chat_id)
    bot.register_next_step_handler(msg, lambda m: get_recipient_address(bot, m, db))

def get_recipient_address(bot: telebot.TeleBot, message: telebot.types.Message, db: Session):
    """
    Receives the recipient address, validates it, and asks for the.
    """
    chat_id = message.chat.id
    recipient_address = message.text.strip()

    if xrpl_wallet.get_account_balance(recipient_address) is None:
        bot.send_message(chat_id, "❌ That recipient address doesn't seem to be valid or activated on the testnet.")
        _send_main_menu(bot, chat_id, "Let's start over. What would you like to do?")
        return
        
    msg = bot.send_message(chat_id, f"✅ Address confirmed. Now, please reply with the amount of XRP you wish to send.")
    bot.register_next_step_handler(msg, lambda m: get_amount_and_send(bot, m, db, recipient_address))

def get_amount_and_send(bot: telebot.TeleBot, message: telebot.types.Message, db: Session, recipient_address: str):
    """
    Receives the amount, validates balance, and executes the transaction.
    """
    tg_id = message.from_user.id
    chat_id = message.chat.id
    
    try:
        amount_to_send_str = message.text.strip()
        
        try:
            amount_to_send = float(amount_to_send_str)
            if amount_to_send <= 0:
                raise ValueError("Amount must be positive.")
        except (ValueError, TypeError):
            bot.send_message(chat_id, "❌ Invalid amount. Please start over.")
            return
            
        sender = crud.get_user_by_telegram_id(db, tg_id=tg_id)
        if not sender:
            bot.send_message(chat_id, "Could not find your user data. Please /start again.")
            return

        bot.send_message(chat_id, "Verifying your balance...")
        sender_balance_drops = xrpl_wallet.get_account_balance(sender.wallet_address)
        
        if sender_balance_drops is None:
            bot.send_message(chat_id, "❌ Could not verify your balance. Please try again later.")
            return
            
        sender_balance_xrp = float(drops_to_xrp(sender_balance_drops))
        available_balance = sender_balance_xrp - 1 # Reserve
        
        if available_balance < amount_to_send:
            bot.send_message(chat_id, f"❌ Insufficient funds. Your available balance is {available_balance:,.6f} XRP.")
            return
            
        bot.send_message(chat_id, "Balance confirmed. Processing your transaction... 🚀")
        
        decrypted_seed = decrypt_seed(sender.encrypted_seed)
        
        
        success = xrpl_wallet.send_xrp(decrypted_seed, str(amount_to_send), recipient_address)

        if success:
            final_message = f"✅ Transaction successful! You sent {amount_to_send} XRP to `{recipient_address}`."
        else:
            final_message = "❌ Transaction failed. The payment could not be processed by the ledger."
            
        bot.send_message(chat_id, final_message, parse_mode="Markdown")
    
    except Exception as e:
        print(f"!!!!!!!!!! ERROR in get_amount_and_send: {e} !!!!!!!!!!")
        bot.send_message(chat_id, "An unexpected error occurred during the transaction.")
    
    finally:
        # --- Guarantees the menu is always shown, even if an error occurs ---
        _send_main_menu(bot, chat_id)
        
def handle_view_tx_history(bot: telebot.TeleBot, chat_id: int, tg_id: int, db: Session):
    """
    Handles 'View Transaction History', fetching and displaying recent transactions.
    """
    user = crud.get_user_by_telegram_id(db, tg_id=tg_id)
    if not user:
        bot.send_message(chat_id, "Please use /start and create a wallet first.")
        return

    bot.send_message(chat_id, "Fetching your transaction history... 📜")

    transactions = xrpl_wallet.get_transaction_history(user.wallet_address)
    
    if not transactions:
        response_text = "You have no recent transactions."
    else:
        response_text = "Here are your last 5 transactions:\n\n"
        for tx in transactions:
            if tx['type'] == 'sent':
                response_text += f"➡️ *Sent* {tx['amount']} XRP\nTo: `{tx['counterparty']}`\n\n"
            else:
                response_text += f"⬅️ *Received* {tx['amount']} XRP\nFrom: `{tx['counterparty']}`\n\n"
    
    bot.send_message(chat_id, response_text, parse_mode="Markdown")
    _send_main_menu(bot, chat_id)

