CONVERSATION_SUMMARY_PROMPT = (
    "Please generate a short summary of the following conversation.\n"
    "If the conversation communicating in Chinese, you should return a Chinese summary.\n"
    "If the conversation communicating in English, you should return an English summary.\n"
    "[Conversation Start]\n"
    "{context}\n"
    "[Conversation End]\n\n"
    "summary:"
)


CONDENSE_TEMPLATE = """
Given the following chat history between Human and AI and a follow up input, rephrase the follow up input so that AI can understand without looking at the chat history.
Chat History:
{context}
Follow Up Input: {input}
Standalone Input:
"""

BOOK_CATEGORY_TEMPLATE = """
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