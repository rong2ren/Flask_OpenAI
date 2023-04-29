import redis
from config import logger # for logging
import os

"""
docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
localhost:8001
docker ps
docker stop redis-stack
docker exec -it redis-stack redis-cli
"""

class RedisClient:
    def __init__(self):
        # Initialize a Redis instance with decode_response set to True
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=os.getenv('REDIS_PORT', 6379),
            db=0,
            decode_responses=True
        )
        self.check_connection()
        if os.getenv('REDIS_REMOVE_ALL_WHEN_START', False):
            self.redis_client.flushall()

    def get_redis_instance(self):
        return self.redis_client

    def check_connection(self):
        # Check if the Redis client object is connected to the Redis cache
        try:
            self.redis_client.ping()
            return True
        except redis.exceptions.ConnectionError as e:
            logger.error(f"Redis: connection failed. {e}")
            return False

    def remove_all(self):
        # Remove all data in the Redis cache
        return self.redis_client.flushall()
    
    def expire_user_session_after(self, user_id, expire_second=3600):
        # expire the user session after expire_second second, default to 1 hour
        # Set expiry only when the key has no expiry
        if self.redis_client.ttl(user_id) == -1:
            self.redis_client.expire(user_id, expire_second)

    def add_book(self, user_id, book):
        """
        Add a book to Redis for the given user ID.
        Returns the number of books added, or 0 if the user ID is not provided.
        """
        if not user_id:
            return 0
        else:
            return self.redis_client.sadd(user_id, book)

    def add_books(self, user_id, book_list):
        """
        Add a list of books to Redis for the given user ID.
        Returns the number of books added, or 0 if the user ID is not provided.
        """
        if not user_id:
            return 0
        else:
            return self.redis_client.sadd(user_id, *book_list)

    def get_num_books(self, user_id):
        # Get the number of books in Redis for the given user ID
        return self.redis_client.scard(user_id)

    def get_books(self, user_id):
        """
        Get the list of books for the given user ID.
        Returns an empty list if no books are found.
        """
        book_list = self.redis_client.smembers(user_id)
        if book_list:
            return book_list
        else:
            return []

    def remove_user(self, user_id):
        # Remove the list of books for the given user ID from Redis.
        return self.redis_client.delete(user_id)
    
# .decode('utf-8')    
