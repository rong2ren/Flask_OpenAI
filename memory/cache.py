
from datastore.datastore import DataStore

class Cache():
    """
    class to store key-value pair into datastore as temporary cache
    """
    def __init__(self, datastore: DataStore):
        self.datastore = datastore

    def check_connection(self):
        # Check if the Redis client object is connected to the Redis cache
        return self.datastore.check_connection()
    
    def expire_user_cache_after(self, user_cache_id, expire_second=3600):
        # expire the user session after expire_second second, default to 1 hour
        # Set expiry only when the key has no expiry
        return self.datastore.expire_cache_after(user_cache_id, expire_second)
    
    def add_conversation_history(self, user_chat_cache_id, message):
        # Add a message to the conversation history for the given user ID.
        if not user_chat_cache_id:
            return 0
        else:
            return self.datastore.rpush_element_to_cache(user_chat_cache_id, message)
    
    def get_conversation_history(self, user_chat_cache_id):
        # Get the conversation history for the given user ID.
        return self.datastore.get_lists(user_chat_cache_id)
    
    def add_book(self, user_cache_id, book):
        """
        Add a book to Redis for the given user ID.
        Returns the number of books added, or 0 if the user ID is not provided.
        """
        if not user_cache_id:
            return 0
        else:
            return self.datastore.add_element_to_cache(user_cache_id, book)

    def add_books(self, user_cache_id, book_list):
        """
        Add a list of books to Redis for the given user ID.
        Returns the number of books added, or 0 if the user ID is not provided.
        """
        if not user_cache_id:
            return 0
        else:
            return self.datastore.add_elements_to_cache(user_cache_id, book_list)
        
    def is_user_cache_exist(self, user_cache_id):
        return self.datastore.is_cache_key_exist(user_cache_id)

    def get_num_books(self, user_cache_id):
        # Get the number of books in Redis for the given user ID
        return self.datastore.get_num_of_elements(user_cache_id)

    def get_books(self, user_cache_id):
        """
        Get the list of books for the given user ID.
        Returns an empty list if no books are found.
        """
        book_list = self.datastore.get_elements(user_cache_id)
        if book_list:
            return book_list
        else:
            return []

    def remove_user_cache(self, user_cache_id):
        # Remove the list of books for the given user ID from Redis.
        return self.datastore.remove_cache(user_cache_id)
    
