"""
# LangChain: Evaluation

## Outline:

* Example generation
* Manual evaluation (and debuging)
* LLM-assisted evaluatio
"""

# Create our QandA application
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import CSVLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.vectorstores import DocArrayInMemorySearch

file = 'OutdoorClothingCatalog_1000.csv'
loader = CSVLoader(file_path=file)
data = loader.load()
index = VectorstoreIndexCreator(
    vectorstore_cls=DocArrayInMemorySearch
).from_loaders([loader])
llm = ChatOpenAI(temperature = 0.0)
qa = RetrievalQA.from_chain_type(
    llm=llm, 
    chain_type="stuff", 
    retriever=index.vectorstore.as_retriever(), 
    verbose=True,
    chain_type_kwargs = {
        "document_separator": "<<<<>>>>>"
    }
)


### Coming up with test datapoints
print(data[10])
print(data[11])
# Hard-coded examples
examples = [
    {
        "query": "Do the Cozy Comfort Pullover Set\
        have side pockets?",
        "answer": "Yes"
    },
    {
        "query": "What collection is the Ultra-Lofty \
        850 Stretch Down Hooded Jacket from?",
        "answer": "The DownTek collection"
    }
]
#LLM-Generated examples
from langchain.evaluation.qa import QAGenerateChain
# QAGenearteChain: will a question and answer pair from each documents
example_gen_chain = QAGenerateChain.from_llm(ChatOpenAI())
new_examples = example_gen_chain.apply_and_parse(
    [{"doc": t} for t in data[:5]]
)
print(new_examples[0])
examples += new_examples
# do a test: only show the final answer, doesn't really know what's going on.
qa.run(examples[0]["query"])

# to help that, manual evaluation
import langchain
langchain.debug = True
# rerun the same example as above, it will printing out more information
qa.run(examples[0]["query"])

# Turn off the debug mode
langchain.debug = False

#above are just for 1 example. How about all of them?
# LLM assisted evaluation
# generate predictions
predictions = qa.apply(examples)

from langchain.evaluation.qa import QAEvalChain
llm = ChatOpenAI(temperature=0)
eval_chain = QAEvalChain.from_llm(llm)
graded_outputs = eval_chain.evaluate(examples, predictions)
for i, eg in enumerate(examples):
    print(f"Example {i}:")
    print("Question: " + predictions[i]['query'])
    print("Real Answer: " + predictions[i]['answer'])
    print("Predicted Answer: " + predictions[i]['result'])
    print("Predicted Grade: " + graded_outputs[i]['text'])
    print()