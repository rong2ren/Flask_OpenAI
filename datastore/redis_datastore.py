
import logging
from typing import Any, Dict, List

import redis
from redis.commands.search.field import TagField, TextField, VectorField
from redis.commands.search.query import Query
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from datastore.datastore import DataStore
from flask_app import logger
"""
SAMPLE_DOCUMENTS = [
    {"text": "Berlin is located in Germany.", "conversation_id": "1", "datetime":20111.232},
]
"""

class RedisDataStore(DataStore):

    def __init__(self):
        self.connect()
        self.index_name = "chat_memory_idx"
        self.create_index()
        existing_vec_num = self.redis_connection.get(f"{self.index_name}-vec_num")
        self.vec_num = int(existing_vec_num.decode("utf-8")) if existing_vec_num else 0

    def connect(self):
        """
        Connect to the Redis server.
        """
        connection_pool = redis.ConnectionPool(
            host="localhost", port="6379", decode_responses=True
        )
        self.redis_connection = redis.Redis(connection_pool=connection_pool)

        # Check redis connection
        try:
            self.redis_connection.ping()
        except redis.exceptions.ConnectionError as e:
            logger.error("FAILED TO CONNECT TO REDIS:", e)
            exit(1)

        # flush data only once after establishing connection
    
    def get_redis_instance(self):
        return self.redis_connection
    
    def check_connection(self) -> bool:
        # Check if the Redis client object is connected to the Redis
        try:
            self.redis_connection.ping()
            return True
        except redis.exceptions.ConnectionError as e:
            logger.error(f"Datastore connection failed: {e}")
            return False
    
    def flush_all(self) -> bool:
        """
        Removes all documents from the redis index.
        """
        return self.redis_connection.flushall()

    # memory1: for saving chat messages
    def create_index(self):
        """
        Creates a Redis index with a vector field.
        """
        try:
            self.redis_connection.ft(f"{self.index_name}").create_index(
                fields=[
                    VectorField(
                        "embedding",
                        "HNSW",
                        {
                            "TYPE": "FLOAT32",
                            "DIM": 1536,
                            "DISTANCE_METRIC": "COSINE",
                            #"INITIAL_CAP": 686,
                            #"M": 40,
                            #"EF_CONSTRUCTION": 200,
                        },
                    ),
                    TextField("text"),  # contains the original message
                    TagField("conversation_id"),  # `conversation_id` for each session
                    TagField("datetime"),
                ],
                definition=IndexDefinition(
                    prefix=[f"{self.index_name}"], index_type=IndexType.HASH
                ),
            )
            logger.info("Created a new Redis index for storing chat history")
        except redis.exceptions.ResponseError as redis_error:
            logger.warning(f"Working with existing Redis index.\nDetails: {redis_error}")
    
    

    def get_all_conversation_ids(self) -> List[str]:
        """
        Returns conversation ids of all conversations.

        Returns:
            List[str]: List of conversation ids stored in redis.
        """
        query = Query("*").return_fields("conversation_id")
        result_documents = self.redis_connection.ft(f"{self.index_name}").search(query).docs

        conversation_ids: List[str] = []
        conversation_ids = list(
            set([getattr(result_document, "conversation_id") for result_document in result_documents])
        )

        return conversation_ids
    
    def index_documents(self, documents: List[Dict]):
        """
        Indexes the set of documents.

        Args:
            documents (List[Dict]): List of documents to be indexed.
        """
        redis_pipeline = self.redis_connection.pipeline(transaction=False)
        for document in documents:
            assert (
                "text" in document and "conversation_id" in document
            ), "Document must include the fields `text`, and `conversation_id`"
            key = f"{self.index_name}:-{self.vec_num}-" + document["conversation_id"]
            redis_pipeline.hset(key, mapping=document)
            self.vec_num += 1
            redis_pipeline.set(f"{self.index_name}-vec_num", self.vec_num)
        redis_pipeline.execute()

    def delete_documents(self, conversation_id: str):
        """
        Deletes all documents for a given conversation id.

        Args:
            conversation_id (str): Id of the conversation to be deleted.
        """
        query = (
            Query(f"""(@conversation_id:{{{conversation_id}}})""")
            .return_fields(
                "id",
            )
            .dialect(2)
        )
        for document in self.redis_connection.ft(f"{self.index_name}").search(query).docs:
            document_id = getattr(document, "id")
            deletion_status = self.redis_connection.ft(f"{self.index_name}").delete_document(document_id, delete_actual_document=True)

            assert deletion_status, f"Deletion of the document with id {document_id} failed!"

    def get_last_documents(self, conversation_id: str, topk: int = 5) -> List[Any]:
        query = (
            Query(f"""(@conversation_id:{{{conversation_id}}})""")
            .sort_by("datetime", False)
            .paging(0, topk)
            .return_fields(
                # parse `result_fields` as strings separated by comma to pass as params
                "conversation_id",
                "text",
                "datetime"
            )
            .dialect(2)
        )
        query_result = self.redis_connection.ft(f"{self.index_name}").search(query).docs
        return query_result

    def get_relevant_documents(
        self,
        query_vector: bytes,
        conversation_id: str,
        topk: int = 5,
    ) -> List[Any]:
        """
        Searches the redis index using the query vector.

        Args:
            query_vector (np.ndarray): Embedded query vector.
            topk (int, optional): Number of results. Defaults to 5.
            result_fields (int, optional): Name of the fields that you want to be
                                           returned from the search result documents

        Returns:
            List[Any]: Search result documents.
        """
        query = (
            Query(
                f"""(@conversation_id:{{{conversation_id}}})=>[KNN {topk} \
                    @embedding $vec_param AS vector_score]"""
            )
            .sort_by("vector_score")
            .paging(0, topk)
            .return_fields(
                # parse `result_fields` as strings separated by comma to pass as params
                "conversation_id",
                "vector_score",
                "text",
            )
            .dialect(2)
        )
        params_dict = {"vec_param": query_vector}
        result_documents = self.redis_connection.ft(f"{self.index_name}").search(query, query_params=params_dict).docs

        return result_documents
    
    def get_stats(self):
        """
        Returns: The stats of the memory index.
        """
        return self.redis_connection.ft(f"{self.index_name}").info()

    def get_num_of_vectors(self):
        return self.vec_num
    
    
    def rpush_element_to_cache(self, key, element):
        if not key:
            return 0
        else:
            return self.redis_connection.rpush(key, element)
        
    def get_lists(self, key):
        if not key:
            return 0
        else:
            #return self.redis_connection.lrange(key, 0, -1) -> all lists
            return self.redis_connection.lrange(key, -10, -1)
            

    # memery 2: for saving books 
    def add_element_to_cache(self, key, element):
        """
        Add a book to Redis for the given user ID.
        Returns the number of books added, or 0 if the user ID is not provided.
        """
        if not key:
            return 0
        else:
            return self.redis_connection.sadd(key, element)

    def add_elements_to_cache(self, key, element_list):
        """
        Add a list of books to Redis for the given user ID.
        Returns the number of books added, or 0 if the user ID is not provided.
        """
        if not key:
            return 0
        else:
            return self.redis_connection.sadd(key, *element_list)
        
    
    def is_cache_key_exist(self, key):
        return self.redis_connection.exists(key)
   

    def get_num_of_elements(self, key):
        # Get the number of books in Redis for the given user ID
        return self.redis_connection.scard(key)

    def get_elements(self, key):
        """
        Get the list of books for the given user ID.
        Returns an empty list if no books are found.
        """
        element_list = self.redis_connection.smembers(key)
        if element_list:
            return element_list
        else:
            return []
    
    def expire_cache_after(self, key, expire_second=3600):
        # expire the user session after expire_second second, default to 1 hour
        # Set expiry only when the key has no expiry
        if self.redis_connection.ttl(key) == -1:
            self.redis_connection.expire(key, expire_second)

    def remove_cache(self, key):
        # Remove the list of books for the given user ID from Redis.
        return self.redis_connection.delete(key)