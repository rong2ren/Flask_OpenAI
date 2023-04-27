# config.py is a module that contains the configuration for the application


from dotenv import load_dotenv
load_dotenv()

# logging configuration
import logging
logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s - %(levelname)s - %(message)s'
    )
logger = logging.getLogger(__name__)

# open ai configuration
COMPLETIONS_MODEL = "text-davinci-003"
EMBEDDINGS_MODEL = "text-embedding-ada-002"
CHAT_MODEL = "gpt-3.5-turbo"
TEXT_EMBEDDING_CHUNK_SIZE=300



