
## Flask
Flask is a micro web framework written in Python. It's designed to be lightweight and flexible, making it a popular choice for building web applications. Flask provides a lot of functionality out of the box, but it's also highly extensible, meaning you can easily add additional libraries and packages to customize your application.
Flask is a lightweight, Python-based web framework used to build web applications and REST APIs.
Flask is similar to Express.js (Node.js backend) in that it provides routing, request handling, and middleware but does not include a frontend.
Uses HTML for UI? Yes, renders HTML via Jinja2 templates

## Redis
Redis is an in-memory data structure store that's often used as a database, cache, and message broker. It's known for its fast read and write speeds, making it a great choice for applications that require high performance. Redis can be used to store a wide range of data types, including strings, lists, sets, and hashes.

## LangChain
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


## Todo:
1. error/exception handling
2. cache expiry and be notified when a session is expired so I can delete from redis
3. more books
4. prompt enginner
5. does langchain use chat or completion
