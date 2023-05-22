from datastore.redis_datastore import RedisDataStore
from memory.memory import RedisMemory
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

#prompt template
system_template = """
You are an helpful AI and expert in books. You job is to give BEST book recommendations.
"""
system_template2 = """
You are an helpful AI.
"""

condense_template = """
Given the following chat history between Human and AI and a follow up input, rephrase the follow up input so that AI can understand without looking at the chat history.
Chat History:
{context}
Follow Up Input: {input}
Standalone Input:
"""

prompt_template = """
You are an AI assistant specialized in books, and your objective is to understand the user's specific requirements for book recommendations through a conversation. 
To achieve this, please follow these step-by-step instructions:
step 1: Carefully read the relevant pieces of previous conversation (delimited by ``` below)
step 2: Carefully read user's input (delimited by <> below)
step 3: Analyze the user's input and relevant pieces of previous conversation to understand their specific requirements in terms of preferred genre, subject, theme, story elements, writing style, target age group, or author.
step 4: When responding to the user, begin by summarizing their specific needs based on the aforementioned aspects. If necessary, ask additional questions to gather more information.

If the user's input is not about books, just let them know that you're here to help with book-related requests only.

Relevant pieces of previous conversation:
```
{context}
```

Current conversation:
User's input: <{input}>
AI:"""

prompt_template2 = """
You are an helpful AI assistant specialized in books, and your objective is to understand the user's specific requirements for book recommendations through a conversation. 

Respond only with a summarization of user's requirements for books in bullet point format, covering all following aspects:
Preferred book type:
Target audience:
Enjoyed books:
Genre preference:
Preferred Subject:
Desired Story elements:
Writing style:

Do NOT recommend books.

Relevant pieces of previous conversation:
```
{context}
```
Carefully read relevant pieces of previous conversation to understand user's previous requirements.
If the user's new requirements input below is not related to books, respond with user's previous requirements.
If the user's new requirements input below indicates a new type of books, add the new information to the existing summarization.

Current conversation:
New requirements input by user: <{input}>
AI:"""


prompt_template3 = """
You are a Book Recommendation AI for a website. Your purpose is to understand user requirements for personalized book recommendations based on user requirements.
Visitors of the website will use you to discover new books to read. You should handle invalid book preferences and provide alternative recommendations.

Here are some commands you can use:
/getRequirement "requirements input by user": Gather the user's requirements for book recommendations. Response only with a summarization of user's requirements in the bullets of preferred genre, subject, theme, story elements, writing style, target age group, and author. Do not recommend books in this command.
/recommend: Generate book recommendations base on user's requirements.

Relevant pieces of previous conversation:
```
{context}
```
Carefully read relevant pieces of previous conversation.

Current conversation:
User's input: <{input}>
AI:"""

_DEFAULT_TEMPLATE = """The following is a friendly conversation between a human and an AI. The AI is talkative and provides lots of specific details from its context. If the AI does not know the answer to a question, it truthfully says it does not know.

Relevant pieces of previous conversation:
{context}

(You do not need to use these pieces of information if not relevant)

Current conversation:
Human: {input}
AI:"""




class ChatWithMemory():
    def __init__(self, datastore):
        self.memory = RedisMemory(datastore, 1)
        #open ai - langchain
        # SystemMessagePromptTemplate.from_template(system_template),
        #    MessagesPlaceholder(variable_name="history"),
        llm_chat = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.0)
        llm_chat_prompt = ChatPromptTemplate.from_messages([
            HumanMessagePromptTemplate.from_template(prompt_template2)
        ])
        self.chat_chain = LLMChain(
                    llm=llm_chat,
                    prompt=llm_chat_prompt,
                    verbose=True,
                )
    
    def create_new_chat(self) -> str:
        return self.memory.create_new_converstaion()
    
    def chat(self, user_input: str, conversation_id: str) -> str:
        contexts = self.memory.get_last_messages(conversation_id)
        #print("\n \033[94m Context: \n")
        contexts_str = ""
        """
        for context in contexts:
            print("\n \033[94m " + context)
        """
        
        if bool(contexts):
            contexts_str = "\n".join(contexts)
    
        ai_response = self.chat_chain.run(input = user_input, context = contexts_str)
        self.memory.save_message(conversation_id, user_input, ai_response)
        #print("\n \033[96m AI: " + ai_response)
        return ai_response




