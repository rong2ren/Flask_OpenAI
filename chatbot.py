# Set your OpenAI API key here
import openai

openai.api_key = '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'
# Initialize conversation history
conversation_history = [
    {"role": "system", "content": "You are a helpful AI assistant."}
]

def chat(user_message):
    # Append user message to conversation history
    conversation_history.append({'role': 'user', 'content': 'user:'+user_message})
    
    # Generate response from GPT-3
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation_history,
    )
    
    bot_message = response.choices[0].message.content
    conversation_history.append({'role': 'user', 'content': 'bot:'+bot_message})

    
    return bot_message



def main():
    while True:
        user_message = input("You: ")
        if user_message.lower() in ['exit', 'quit']:
            break
        response = chat(user_message)
        print(f"Bot: {response}")

main()