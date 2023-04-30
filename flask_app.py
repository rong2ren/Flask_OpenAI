from config import DevelopmentConfig, ProductionConfig
import os
from flask import Flask
import logging

def create_flask_app():
    config_by_name = dict(
        dev=DevelopmentConfig,
        prod=ProductionConfig
    )
    config_name = os.getenv('APP_ENV', 'dev')

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Logging configuration
    LOG_LEVEL_MAP = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'INFO')
    """
    1. The defulat logging format for flask is:
    %(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]
    2. The default logging level for Flask logger is WARNING, 
    which means that only warning messages and above (error and critical) will be logged.

    Or you can config by
    logging.basicConfig(
        level=LOG_LEVEL_MAP.get(LOGGING_LEVEL, logging.INFO),
        format = '%(asctime)s - %(levelname)s - %(message)s'
    )
    """
    app.logger.setLevel(LOG_LEVEL_MAP.get(LOGGING_LEVEL, logging.WARNING))
    return app

app = create_flask_app()    
logger = app.logger
