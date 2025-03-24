import json
from uuid import uuid4
from dify_client import ChatClient

api_key = "app-k7zVTBJvxJ4U4bfoWeLg3YMH"
# Initialize ChatClient
chat_client = ChatClient(api_key)

def get_dify_parameters(user_id):
    parameters = chat_client.get_application_parameters(user=user_id)
    parameters.raise_for_status()
    parameters = json.loads(parameters.text)

    print(parameters)

def get_list_of_converstations(user_id, show_message = False):
    conversations = chat_client.get_conversations(user=user_id)
    conversations.raise_for_status()
    conversations_json = json.loads(conversations.text)

    if 'data' in conversations_json:
        converstaion_data = conversations_json.get('data')
        num_of_converstaion = len(converstaion_data)
        print('number of conversations:', num_of_converstaion)
        for data in converstaion_data:
            conversation_id = data.get('id')
            print('conversation id:', conversation_id)
            if show_message:
                messages = chat_client.get_conversation_messages(user=user_id, conversation_id=conversation_id)
                messages.raise_for_status()
                messages_json = json.loads(messages.text)
                if 'data' in messages_json:
                    for text in messages_json.get('data'):
                        print('User:', text.get('query'))
                        print('AI:', text.get('answer'))

def call_dify_api(user_input, user_id, conversation_id):
    if converstaion_id:
        chat_response = chat_client.create_chat_message(inputs={}, query=user_input, user=user_id, conversation_id=converstaion_id, response_mode="streaming")
    else:
        chat_response = chat_client.create_chat_message(inputs={}, query=user_input, user=user_id, response_mode="streaming")
    chat_response.raise_for_status()

    for line in chat_response.iter_lines(decode_unicode=True):
        line = line.split('data:', 1)[-1] #splits the line at the first occurrence of 'data:' and keeps the portion after it.
        if line.strip():
            line = json.loads(line.strip())
            converstaion_id = line.get('conversation_id')
            answer = line.get('answer')
            if answer:
                print(answer, end='')





    


    
    

    

