import logging
import numpy as np
from uuid import uuid4
from typing import Any, Dict, List
import time

from datastore.datastore import DataStore
from langchain.embeddings.openai import OpenAIEmbeddings
from flask_app import logger



class Memory():
    """
    class to store embeddings into the datastore
    Sample to save into the datastore:
        {"text": "Berlin is located in Germany.", "conversation_id": "1", "datetime":20111.232}
    """

    def __init__(self, datastore: DataStore, topk: int = 5):
        self.datastore = datastore
        self.topk = topk
        self.embed_client = OpenAIEmbeddings()
        
        
    def create_new_converstaion(self) -> str:
        """
        create a new conversation. converestaion_id is returned
        Returns:
            str: conversation id
        """
        conversation_id = uuid4().hex
        return conversation_id
    
    def delete_conversation(self, conversation_id: str) -> None:
        """
        Deletes all chat history for a given conversation id.

        Args:
            conversation_id (str): Id of the conversation to be deleted.
        """
        self.datastore.delete_documents(conversation_id)
    
    def save_message(self, conversation_id: str, human: str, assistant: str) -> None:
        """
        Adds a message to a conversation chat history.

        Args:
            conversation_id (str): ID of the conversation to add the message to.
            human (str): User message.
            assistant (str): Assistant message.
        """
        text = f"User: {human}\nAI: {assistant}"
        document: Dict = {"text": text, "conversation_id": conversation_id, "datetime": time.time()}
        #get embedding for the text
        text_embedding = self.embed_client.embed_query(text)
        document["embedding"] = np.array(text_embedding).astype(np.float32).tobytes()
        self.datastore.index_documents(documents=[document])

    def get_last_messages(self, conversation_id: str) -> List[Any]:
        documents = self.datastore.get_last_documents(
            conversation_id=conversation_id, topk=self.topk
        )
       
        messages = [d["text"] for d in documents]
        return messages
    
    def get_relevant_messages(self, conversation_id: str, query: str) -> List[Any]:
        """
        Gets the messages of a conversation using the query message.

        Args:
            conversation_id (str): ID of the conversation to get the messages of.
            query (str): Current user message you want to pull history for to use in the prompt.
            topk (int): Number of messages to be returned. Defaults to 5.

        Returns:
            List[Any]: List of messages of the conversation.
        """
        query_embedding = self.embed_client.embed_query(query)
        query_vector = np.array(query_embedding).astype(np.float32).tobytes()
        documents = self.datastore.get_relevant_documents(
            query_vector=query_vector, conversation_id=conversation_id, topk=self.topk
        )
       
        messages = [d["text"] for d in documents]
        return messages
    
    