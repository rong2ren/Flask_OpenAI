from flask import Flask
import logging
from config import Config


def create_flask_app():

    app = Flask(__name__)
    # Logging configuration
    app.config.from_object(Config)
    
    LOG_LEVEL_MAP = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
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
    app.logger.setLevel(LOG_LEVEL_MAP.get(app.config.get('LOGGING_LEVEL', 'WARNING')))
    return app

app = create_flask_app()    
logger = app.logger
