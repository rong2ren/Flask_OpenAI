import os  # for reading API key
import openai  # used for calling the OpenAI API
import tiktoken # for counting tokens
import time # for measuring time duration of API calls
from config import logger # for logging

# load OpenAI API key from .env file
openai.api_key = os.getenv("OPENAI_API_KEY")

def openai_completion(prompt, model = "text-davinci-003", max_tokens = 256, temperature = 0.0):
    if not prompt:
        logger.error("OpenAI: No prompt provided.")
        return None
    
    try:
        logger.info(f"OpenAI: Send request to ChatGPT Compleition API: {model}")
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
        logger.info(f"OpenAI: Full response received {response_time:.2f} seconds after request. Number of token usage: {completion.usage.total_tokens}")
        #print(f"Full text received: {completion_text}")
        return completion_text.strip()
    except openai.error.APIError as e:
        logger.error(f"OpenAI: OpenAI API returned an API Error: {e}")
        return None
    except openai.error.RateLimitError as e:
        logger.error(f"OpenAI: OpenAI API request exceeded rate limit: {e}")
        return None
    except Exception as e:
        # catching naked exceptions is bad practice, but in this case we'll log & save them
        logger.error(f"OpenAI: ChatGPT Chat Completion API Request failed with Exception {e}")
        return None

def openai_chat_completion(messages, model = "gpt-3.5-turbo", max_tokens = 256, temperature = 0.0):
    if not messages:
        logger.error("OpenAI: No messages provided.")
        return None
    if not model:
        model = "gpt-3.5-turbo"
    
    try:
        num_tokens = num_tokens_from_messages(messages, model)
        logger.info(f"OpenAI: Send request to ChatGPT Chat Compleition API: {model}. Number of token sent: {num_tokens}")
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
        logger.info(f"OpenAI: Full response received {response_time:.2f} seconds after request. Number of token: {completion.usage.total_tokens}")
        return completion.choices[0].message.content.strip()
    except openai.error.APIError as e:
        logger.error(f"OpenAI: OpenAI API returned an API Error: {e}")
        return None
    except openai.error.RateLimitError as e:
        logger.error(f"OpenAI: OpenAI API request exceeded rate limit: {e}")
        return None
    except Exception as e:
        # catching naked exceptions is bad practice, but in this case we'll log & save them
        logger.error(f"OpenAI: ChatGPT Chat Completion API Request failed with Exception {e}")
        return None

def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        logger.warning("tiktoken: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    
    if model == "gpt-3.5-turbo":
        logger.info("tiktoken: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301.")
        model="gpt-3.5-turbo-0301"
    elif model == "gpt-4":
        logger.info("tiktoken: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314.")
        model="gpt-4-0314"
    
    model_data = {
        "gpt-3.5-turbo-0301": {"tokens_per_message": 4, "tokens_per_name": 0},
        "gpt-4-0314": {"tokens_per_message": 3, "tokens_per_name": 1},
    }
    if model in model_data:
        tokens_per_message = model_data[model]["tokens_per_message"]
        tokens_per_name = model_data[model]["tokens_per_name"]
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