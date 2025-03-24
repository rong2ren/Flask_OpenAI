"""
user input: tell me what TVs are for sale

Step 1: evaluation the input to make sure it doesnt contain any inappropriate content
Step 2: identify the input: what type of query it is. in this case, it is a product inquery
Step 3: retrieve information and use llm to write helpful response
Step 4: check the output
"""

import os
import openai
import tiktoken
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

openai.api_key  = os.environ['OPENAI_API_KEY']

#llm
"""
A language model is built by using supervised learning (x->y) to repeatedly predict the next word.

Two types of LLMs.
- Base LLM: predicts next word, base on text training data
query: 'what is the capital of France'
it will return the other list of questions about Frances
- Instruction Tuned LLM: tried to follow instructions
query: 'What is the capital of France?'
it will return 'The capital of France is Paris'

Getting from a Base LLM to an instruction tuned LLM:
1. Train a Base LLM on a lot of data
2. Further train the model:
    - Fine-tune on examples of where the output follows an input instruction
    - Obtain human-ratings of the quality of different LLM outputs, on criteria such as whether it is helpful, honest and harmless
    - Tune LLM to increase probability that it generates the morehighly rated outputs (using RLHF: Reinforcement Learning from Human Feedback)
"""
def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message["content"]
response = get_completion("What is the capital of France?")
print(response)


# Tokens: treat commonly occuring sequences of character as tokens
# lollipop will be break down into: l  oll ipop 
# put dash in between letters, llm will break it into each character as a token
response = get_completion("Take the letters in lollipop \
and reverse them")
print(response) # the response will be wrong: ppilolol 
response = get_completion("""Take the letters in \
l-o-l-l-i-p-o-p and reverse them""")
print(response)




def get_completion_from_messages(messages, 
                                 model="gpt-3.5-turbo", 
                                 temperature=0, 
                                 max_tokens=500):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature, # this is the degree of randomness of the model's output
        max_tokens=max_tokens, # the maximum number of tokens the model can ouptut 
    )
    return response.choices[0].message["content"]

messages =  [  
{'role':'system', 
 'content':"""You are an assistant who\
 responds in the style of Dr Seuss."""},    
{'role':'user', 
 'content':"""write me a very short poem\
 about a happy carrot"""},  
] 
response = get_completion_from_messages(messages, temperature=1)
print(response)


def get_completion_and_token_count(messages, 
                                   model="gpt-3.5-turbo", 
                                   temperature=0, 
                                   max_tokens=500):
    
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature, 
        max_tokens=max_tokens,
    )
    
    content = response.choices[0].message["content"]
    
    token_dict = {
'prompt_tokens':response['usage']['prompt_tokens'],
'completion_tokens':response['usage']['completion_tokens'],
'total_tokens':response['usage']['total_tokens'],
    }

    return content, token_dict

messages = [
{'role':'system', 
 'content':"""You are an assistant who responds\
 in the style of Dr Seuss."""},    
{'role':'user',
 'content':"""write me a very short poem \ 
 about a happy carrot"""},  
] 
response, token_dict = get_completion_and_token_count(messages)
print(response)
print(token_dict)
