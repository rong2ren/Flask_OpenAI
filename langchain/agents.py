"""
LangChain: Agents¶
Outline:
Using built in LangChain tools: 
- DuckDuckGo search and Wikipedia
- Defining your own tools
"""
# Built-in LangChain tools
#!pip install -U wikipedia
from langchain.agents.agent_toolkits import create_python_agent
from langchain.agents import load_tools, initialize_agent
from langchain.agents import AgentType
from langchain.tools.python.tool import PythonREPLTool
from langchain.python import PythonREPL
from langchain.chat_models import ChatOpenAI

#We need to set the temperature to 0, because we will use the llm as the reasoning agent, connecting to other sources and data
llm = ChatOpenAI(temperature=0)
#2 tools: llm-math and wikipedia (run search queries against wikipedia and return result)
tools = load_tools(["llm-math","wikipedia"], llm=llm)
#CHAT_ZERO_SHOT_REACT_DESCRIPTION -> 
agent= initialize_agent(
    tools, 
    llm, 
    agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True, #when llm may output something that cannot parsed, it will ask llm to correct itself
    verbose = True)
agent("What is the 25% of 300?")
"""
Thought: We need to calculate 25% of 300, which involves multiplication and division
Action:
{
    "action": "Calculator,
    "action_input": "300*0.25"
}

Observation: Answer: 75.0
Thought: We have the answer to the question.

Final answer: 75.0
"""


question = "Tom M. Mitchell is an American computer scientist \
and the Founders University Professor at Carnegie Mellon University (CMU)\
what book did he write?"
result = agent(question) 


#Python agent
agent = create_python_agent(
    llm,
    tool=PythonREPLTool(),
    verbose=True
)
customer_list = [["Harrison", "Chase"], 
                 ["Lang", "Chain"],
                 ["Dolly", "Too"],
                 ["Elle", "Elem"], 
                 ["Geoff","Fusion"], 
                 ["Trance","Former"],
                 ["Jen","Ayai"]
                ]
agent.run(f"""Sort these customers by \
last name and then first name \
and print the output: {customer_list}""") 

#### View detailed outputs of the chains
import langchain
langchain.debug=True
agent.run(f"""Sort these customers by \
last name and then first name \
and print the output: {customer_list}""") 
langchain.debug=False



# Define your own tool
#!pip install DateTime
from langchain.agents import tool
from datetime import date

@tool
def time(text: str) -> str:
    """Returns todays date, use this for any \
    questions related to knowing todays date. \
    The input should always be an empty string, \
    and this function will always return todays \
    date - any date mathmatics should occur \
    outside this function."""
    return str(date.today())

agent= initialize_agent(
    tools + [time], 
    llm, 
    agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True,
    verbose = True)

"""
**Note**: 

The agent will sometimes come to the wrong conclusion (agents are a work in progress!). 

If it does, please try running it again.
"""
try:
    result = agent("whats the date today?") 
except: 
    print("exception on external access")