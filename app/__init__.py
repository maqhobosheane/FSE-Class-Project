from flask import Flask
from config import config

# Initialize Flask app
flask_app = Flask(__name__)
flask_app.config.from_object(config)

# Import routes first (this will create the bot and register handlers)
from app import routes