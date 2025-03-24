"""
LangChain: Memory
Outline
- ConversationBufferMemory:
This memory allows for storing of messages and then exacts the messages in a variable
- ConversationBufferWindowMemory:
This memory keeps a list of the interactions of the converstion over time. It only uses the last k interactions
- ConversationTokenBufferMemory:
This memory keeps a buffer of recent interactiosn in memory, and uses token length rather than number of interactions to determine when to flush interactions
- ConversationSummaryMemory:
This memory creates a summary of the converstaion over time
- Vector data memory:
Store text (from converstaion or elsewhere) in a vector database and retrieves the most relevant blocks of text
- Entity memory:
Using an LLM, it remembers details about specific entities.

You can use multiple memories at one time. 
e.g. converstaion memory + entity memory to recall for example, books or individuals
You can also store the conversation in a conventional database (such as key-value store or SQL)
"""
## ConversationBufferMemory
import os

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

import warnings
warnings.filterwarnings('ignore')

from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
llm = ChatOpenAI(temperature=0.0)
memory = ConversationBufferMemory()
conversation = ConversationChain(
    llm=llm, 
    memory = memory,
    verbose=True
)
conversation.predict(input="Hi, my name is Andrew")
conversation.predict(input="What is 1+1?")
conversation.predict(input="What is my name?")
print(memory.buffer)
memory.load_memory_variables({})

#more details
memory = ConversationBufferMemory()
memory.save_context({"input": "Hi"}, 
                    {"output": "What's up"})
print(memory.buffer)
memory.load_memory_variables({})
memory.save_context({"input": "Not much, just hanging"}, 
                    {"output": "Cool"})
memory.load_memory_variables({})


## ConversationBufferWindowMemory
from langchain.memory import ConversationBufferWindowMemory
llm = ChatOpenAI(temperature=0.0)
memory = ConversationBufferWindowMemory(k=1)
conversation = ConversationChain(
    llm=llm, 
    memory = memory,
    verbose=False
)
memory.save_context({"input": "Hi"},
                    {"output": "What's up"})
memory.save_context({"input": "Not much, just hanging"},
                    {"output": "Cool"})
memory.load_memory_variables({})


## ConversationTokenBufferMemory
from langchain.memory import ConversationTokenBufferMemory
from langchain.llms import OpenAI
llm = ChatOpenAI(temperature=0.0)
memory = ConversationTokenBufferMemory(llm=llm, max_token_limit=30)
memory.save_context({"input": "AI is what?!"},
                    {"output": "Amazing!"})
memory.save_context({"input": "Backpropagation is what?"},
                    {"output": "Beautiful!"})
memory.save_context({"input": "Chatbots are what?"}, 
                    {"output": "Charming!"})
memory.load_memory_variables({})

## ConversationSummaryMemory
from langchain.memory import ConversationSummaryBufferMemory

# create a long string
schedule = "There is a meeting at 8am with your product team. \
You will need your powerpoint presentation prepared. \
9am-12pm have time to work on your LangChain \
project which will go quickly because Langchain is such a powerful tool. \
At Noon, lunch at the italian resturant with a customer who is driving \
from over an hour away to meet you to understand the latest in AI. \
Be sure to bring your laptop to show the latest LLM demo."

memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=100)
memory.save_context({"input": "Hello"}, {"output": "What's up"})
memory.save_context({"input": "Not much, just hanging"},
                    {"output": "Cool"})
memory.save_context({"input": "What is on the schedule today?"}, 
                    {"output": f"{schedule}"})
memory.load_memory_variables({})
conversation = ConversationChain(
    llm=llm, 
    memory = memory,
    verbose=True
)
conversation.predict(input="What would be a good demo to show?")
memory.load_memory_variables({})

