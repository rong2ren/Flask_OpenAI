import os  # for reading API key
import openai  # used for calling the OpenAI API
from dotenv import load_dotenv
import tiktoken
import  time # for measuring time duration of API calls
import logging

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def openai_completion(model, prompt, max_tokens, temperature):
    if not model:
        model = "text-davinci-003"
    print(f"Send request to ChatGPT Compleition API: {model}")
    # record the time before the request is sent
    start_time = time.time()
    completion = openai.Completion.create(
            mode = model,
            prompt = prompt,
            temperature = temperature,
            max_tokens = max_tokens
    )
    # calculate the time it took to receive the response
    response_time = time.time() - start_time

    # extract the text from the response
    completion_text = completion.choices[0].text

    # print the time delay and text received
    print(f"Full response received {response_time:.2f} seconds after request. Number of token usage: {completion.usage.total_tokens}")
    #print(f"Full text received: {completion_text}")
    return completion_text.strip()


def openai_chat_completion(model, messages, max_tokens, temperature):
    if not model:
        model = "gpt-3.5-turbo"
    num_tokens = num_tokens_from_messages(messages, model)
    print(f"Send request to ChatGPT Chat Compleition API: {model}. Number of token sent: {num_tokens}")
    # record the time before the request is sent
    start_time = time.time()
    completion = openai.ChatCompletion.create(
            model = model,
            messages = messages,
            temperature = temperature,
            max_tokens= max_tokens,
    )
    # calculate the time it took to receive the response
    response_time = time.time() - start_time
    # print the time delay and completion token
    print(f"Full response received {response_time:.2f} seconds after request. Number of token: {completion.usage.total_tokens}")
    #print(f"Full response received:\n{completion}")

    return completion.choices[0].message.content.strip()

def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("tiktoken - Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        print("tiktoken - Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301")
    elif model == "gpt-4":
        print("tiktoken - Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314.")
        return num_tokens_from_messages(messages, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(f"tiktoken - num_tokens_from_messages() is not implemented for model {model}.")
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens



