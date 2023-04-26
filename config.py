# config.py is a module that contains the configuration for the application

# logging configuration
import logging
logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s - %(levelname)s - %(message)s'
    )
logger = logging.getLogger(__name__)

from dotenv import load_dotenv
load_dotenv()
