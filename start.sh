#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Run Database Initialization
echo "Running database initialization..."
python -c "from app.database.session import engine; from app.database.models import Base; Base.metadata.create_all(bind=engine); print('Database tables created successfully')"

# Set Telegram Webhook
echo "Setting Telegram webhook..."
python -c "import requests, os; token = os.getenv('TELEGRAM_BOT_TOKEN'); webhook_url = os.getenv('WEBHOOK_URL') + '/telegram-webhook'; response = requests.post(f'https://api.telegram.org/bot{token}/setWebhook', json={'url': webhook_url}); print('Webhook set:', response.json())"

# Start the Gunicorn server
echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8080 run:flask_app