from abc import ABC, abstractmethod
from typing import Any, Dict, List

class DataStore(ABC):
    """
    A datastore class.
    """

    @abstractmethod
    def connect(self):
        """
        connect to the underlying datastore, redis or pinecone
        """
        raise NotImplementedError

    @abstractmethod
    def flush_all(self) -> bool:
        """
        Removes all documents from the datastore.
        """
        raise NotImplementedError

    @abstractmethod
    def create_index(self):
        """
        Creates a index with a vector field. -> for chat history
        """
        raise NotImplementedError
    
    @abstractmethod
    def index_documents(self, documents: List[Dict]):
        """
        Indexes the set of documents.

        Args:
            documents (List[Dict]): List of documents to be indexed.
        """
        raise NotImplementedError
    
    @abstractmethod
    def delete_documents(self, conversation_id: str):
        """
        Deletes all documents for a given conversation id.

        Args:
            conversation_id (str): Id of the conversation to be deleted.
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_last_documents(self, conversation_id: str, topk: int = 5) -> List[Any]:
        """
        Gets the last messages of a conversation

        Args:
            conversation_id (str): ID of the conversation to get the messages of.
            topk (int): Number of messages to be returned.

        Returns:
            List[Any]: List of messages of the conversation.
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_relevant_documents(self, query_vector: bytes, conversation_id: str, topk: int = 5) -> List[Any]:
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
        raise NotImplementedError





    @abstractmethod
    def add_element_to_cache(self, key, element):
        """
        Add a book to Redis for the given user ID.
        Returns the number of books added, or 0 if the user ID is not provided.
        """
        raise NotImplementedError
    
    @abstractmethod
    def add_elements_to_cache(self, key, element_list):
        """
        Add a list of books to Redis for the given user ID.
        Returns the number of books added, or 0 if the user ID is not provided.
        """
        raise NotImplementedError
    
    @abstractmethod
    def is_cache_key_exist(self, key):
        raise NotImplementedError
    
    @abstractmethod
    def get_num_of_elements(self, key):
        # Get the number of books in Redis for the given user ID
        raise NotImplementedError
    
    @abstractmethod
    def get_elements(self, key):
        """
        Get the list of books for the given user ID.
        Returns an empty list if no books are found.
        """
        raise NotImplementedError
    
    @abstractmethod
    def expire_cache_after(self, key, expire_second=3600):
        # expire the user session after expire_second second, default to 1 hour
        # Set expiry only when the key has no expiry
        raise NotImplementedError
    
    @abstractmethod
    def remove_cache(self, key):
        # Remove the list of books for the given user ID from datastore.
        raise NotImplementedError