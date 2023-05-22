import os

class Config:
    # Flask configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    if not SECRET_KEY:
        raise Exception("FLASK_SECRET_KEY environment variable is not set")
    DEBUG = os.getenv('APP_DEBUG', False)

    # Any remote API (OpenAI, Cohere etc.)
    OPENAI_TIMEOUT = float(os.getenv("REMOTE_API_TIMEOUT_SEC", 30))
    OPENAI_BACKOFF = float(os.getenv("REMOTE_API_BACKOFF_SEC", 10))
    OPENAI_MAX_RETRIES = int(os.getenv("REMOTE_API_MAX_RETRIES", 5))

    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Data store (Redis, Pinecone, etc.)
    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = int(os.getenv("REDIS_PORT"))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

    # Logger
    LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'INFO').upper()
