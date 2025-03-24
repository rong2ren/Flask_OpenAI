from datastore.redis_datastore import RedisDataStore
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
from prompt.prompt import test
from memory.memory import Memory
from memory.cache import Cache


datastore = RedisDataStore()
memory = Memory(datastore, 3)
#open ai - langchain
# SystemMessagePromptTemplate.from_template(system_template),
#    MessagesPlaceholder(variable_name="history"),
llm_chat = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.0)
llm_chat_prompt = ChatPromptTemplate.from_messages([
    HumanMessagePromptTemplate.from_template(test)
])
chat_chain = LLMChain(
            llm=llm_chat,
            prompt=llm_chat_prompt,
            verbose=True,
                )



conversation_id = memory.create_new_converstaion()

while True:
    # Prompt the user for input
    user_input = input("\n \033[92m Human: ")
    ai_response = "ok"
    
    """
    Allows user to chat with user by leveraging the infinite contextual memor for fetching and
        adding historical messages to the prompt to the ChatGPT model.
    """
    contexts = memory.get_relevant_messages(conversation_id, user_input)
    print("\n \033[94m Context: \n")
    contexts_str = ""
    for context in contexts:
        print("\n \033[94m " + context)
    if bool(contexts):
        contexts_str = "\n\n".join(contexts)
    else:
        contexts_str = ""
    
    ai_response = chat_chain.run(input = user_input, context = contexts_str)
    memory.save_message(conversation_id, user_input, ai_response)

    print("\n \033[96m AI: \n" + ai_response)