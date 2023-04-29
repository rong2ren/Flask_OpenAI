#This file contains most of the configuration variables that the app needs.

from flask import Flask
import logging
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ['FLASK_SECRET_KEY']

class ProductionConfig(Config):
    DEBUG = False

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class TestingConfig(Config):
    TESTING = True


# Create the Flask application
app = Flask(__name__)
# NOTE: The secret key is used to cryptographically-sign the cookies used for storing
#       the session identifier.
# Flask-Session won't work without a secret key; it's important to set this to a random string of characters.
app.secret_key = os.environ.get('FLASK_SECRET_KEY')
# Enable Flask's debug mode if the DEBUG environment variable is set
app.config['FLASK_DEBUG'] = os.environ.get('FLASK_DEBUG', False)

# Initialize logger - will use Flask's built-in logger
LOG_LEVEL_MAP = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

logging.basicConfig(
    level=LOG_LEVEL_MAP.get(os.getenv('LOGGING_LEVEL'), logging.INFO),
    format = '%(asctime)s - %(levelname)s - %(message)s'
    )
logger = app.logger
"""
# 2nd option: create a new logger

logger = logging.getLogger(__name__)
"""