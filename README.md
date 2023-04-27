

## resources
https://github.com/hwchase17/langchain/tree/c2d1d903fa35b91018b4d777db2b008fcbaa9fbc


## converstion history:
Yes, that requires a some application coding, often a database with a table for:

User (if more than one user will be accessing your app)
Chat Topics (where you will keep the description of the chat, the chatid, etc)
Chat Messages (messages, where you will store the chatid, role, content and any and all API params you might want to save, for whatever reason (debugging, etc)).


1. https://github.com/stancsz/chatgpt/
2. https://stackoverflow.com/questions/74711107/openai-api-continuing-conversation
3. langchain: https://python.langchain.com/en/latest/modules/memory/how_to_guides.html
4. https://github.com/olahsymbo/interview-ai-gpt3
5. https://github.com/continuum-llms/chatgpt-memory/blob/main/chatgpt_memory/utils/reflection.py
6. 