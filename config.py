#This file contains most of the flask configuration variables that the app needs.
import os

class Config:
    # Flask configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False





