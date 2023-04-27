import uuid
import redis
import os  # for reading redis config

"""
Not used anymore! Use RedisConn.py instead!
"""


def connect_to_redis():
    redis_client = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=os.getenv('REDIS_PORT', 6379),
        db = 0,
        decode_responses=True
    )
    if redis_client.ping():
        redis_client.flushall() #remove all existing keys from Redis
        return redis_client
    else:
        print("Redis: failed to connect to Redis")
        return None

def check_redis_connection(redis_client):
    return redis_client.ping()

def remove_all_from_redis(redis_client):
    return redis_client.flushall()

def generate_user_id():
    # Generate a unique user ID.
    """
    #another way for user_id:
    timestamp = int(time.time())
    random_value = uuid.uuid4().hex[:6] # Generate a random hex string of length 6
    return f"user_{timestamp}_{random_value}"
    """
    return str(uuid.uuid4())

def add_1_book_to_redis(redis_client, user_id, book):
    """
    Add one books to Redis for the given user ID.
    Returns num of books added, or raises an exception if the user ID is not provided.
    """
    if not user_id:
        #raise ValueError("Redis: User ID not provided")
        return 0
    else:
        return redis_client.sadd(user_id, book)

def add_books_to_redis(redis_client, user_id, book_list):
    """
    Add a list of books to Redis for the given user ID.
    Returns 1 if the operation was successful, or raises an exception if the user ID is not provided.
    """
    if not user_id:
        #raise ValueError("Redis: User ID not provided")
        return 0
    else:
        #num_of_books = 0
        #for book in book_list:
        #    num_of_books += redis_client.sadd(user_id, book)
        #return num_of_books
        return redis_client.sadd(user_id, *book_list)
    
def get_number_of_books_for_userid(redis_client, user_id):
    return redis_client.scard(user_id)

def get_books_from_redis(redis_client, user_id):
    """
    Get the list of books for the given user ID.
    Returns an empty list if no books are found.
    """
    return redis_client.smembers(user_id)
    

def remove_user_from_redis(redis_client, user_id):
    # Remove the list of books for the given user ID from Redis.
    redis_client.delete(user_id)

def test():

    # Generate a user ID
    user_id = generate_user_id()
    redis_client = connect_to_redis()

    #redis_client.set(user_id, ",".join(book_list))
    #book_list = redis_client.get(user_id)

    # Add a list of books to Redis for a user
    book_list = ["Book 1", "Book 2", "Book 3"]
    add_books_to_redis(redis_client, user_id, book_list)

    # Get the list of books from Redis for a user
    books = get_books_from_redis(redis_client, user_id)
    for book in books:
        print(book)

    # Remove the list of books from Redis for a user
    remove_user_from_redis(redis_client, user_id)



