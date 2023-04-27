import redis
import os
import uuid
#from config import logger # for logging

class RedisClient:
    def __init__(self):
        # Initialize a Redis client object
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=os.getenv('REDIS_PORT', 6379),
            db=0,
            decode_responses=True
        )
        if self.redis_client.ping():
            self.redis_client.flushall()
        else:
            print("Redis: failed to connect to Redis")

    def check_connection(self):
        # Check if the Redis client object is connected to the Redis cache
        return self.redis_client.ping()

    def remove_all(self):
        # Remove all data in the Redis cache
        return self.redis_client.flushall()
    
    def create_user_session(self): 
        return str(uuid.uuid4())
    
    def expire_user_session_after(self, user_id, expire_second=3600):
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