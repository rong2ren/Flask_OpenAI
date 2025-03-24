"""
LangChain: Q&A over Documents
An example might be a tool that would allow you to query a product catalog for items of interest.
"""

#pip install --upgrade langchain
import os

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import CSVLoader
from langchain.vectorstores import DocArrayInMemorySearch
from IPython.display import display, Markdown

file = 'OutdoorClothingCatalog_1000.csv'
loader = CSVLoader(file_path=file)

from langchain.indexes import VectorstoreIndexCreator
#pip install docarray
index = VectorstoreIndexCreator(
    vectorstore_cls=DocArrayInMemorySearch
).from_loaders([loader])

query ="Please list all your shirts with sun protection \
in a tab le in markdown and summarize each one."
response = index.query(query)
display(Markdown(response))

"""
LLM's can only inspect a few thousand words at a time
Embedding create numeric representations of the text
Embedding vector captures content/meaning
Text with similar content will have similar vectors

docs -> smaller chunks -> embedding for each chunks -> save into embedding vector
query -> embedding for a query -> pick the most similar in the vectro database to the query
"""


loader = CSVLoader(file_path=file)
docs = loader.load() #load documents from the document loader
print(docs[0])
from langchain.embeddings import OpenAIEmbeddings
embeddings = OpenAIEmbeddings()
# below shows how to embed a query
embed = embeddings.embed_query("Hi my name is Harrison")
print(len(embed)) #1536
print(embed[:5])

# create embedding for the documents 
db = DocArrayInMemorySearch.from_documents(
    docs, 
    embeddings
)
query = "Please suggest a shirt with sunblocking"
docs = db.similarity_search(query)
print(len(docs)) #4
print(docs[0]) # look at the first one


"""
Q&A for the documents
retriever from the vector store
"""
retriever = db.as_retriever()
llm = ChatOpenAI(temperature = 0.0)
# combine the documents into a single piece of context into qdocs varaible
qdocs = "".join([docs[i].page_content for i in range(len(docs))])

response = llm.call_as_llm(f"{qdocs} Question: Please list all your \
shirts with sun protection in a table in markdown and summarize each one.") 
display(Markdown(response))

# above are doing it manually
# all above steps can be done by RetrievalQA Chain
"""
- Stuff method
Stuffing is the simplest method. You simply stuff all data into the prompts as context to pass to the language model
Pros: It makes a single call to the LLM. the LLM has access to all the data at once.
Cons: LLMs have a context length, and for large documents or many documents this will not work as it will result in a prompt larger than the context length.

- Map_reduce: 
retrieve documents as independent and each documents to additional LLMs.

- Refine: 

- Map-rerank

"""
qa_stuff = RetrievalQA.from_chain_type(
    llm=llm, 
    chain_type="stuff", 
    retriever=retriever, 
    verbose=True
)
query =  "Please list all your shirts with sun protection in a table \
in markdown and summarize each one."
response = qa_stuff.run(query)
display(Markdown(response))


# remember above, we can just do one line to do the same thing as RetrievalQA chain
response = index.query(query, llm=llm)
print(response)


# swap the cls to different vector store
index = VectorstoreIndexCreator(
    vectorstore_cls=DocArrayInMemorySearch,
    embedding=embeddings,
).from_loaders([loader])