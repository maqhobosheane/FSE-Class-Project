from flask import Flask
from config import config

# Initialize Flask app
flask_app = Flask(__name__)
flask_app.config.from_object(config)

# Import bot first
from app.bot import bot

# Import routes to register them with the app
from app import routes