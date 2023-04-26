from flask import Flask, render_template, request, jsonify, url_for
from api.openai_api import openai_chat_completion
from api.booklibrary_api import openlibary_search
import asyncio # for running API calls concurrently
from config import logger # for logger
import aiohttp

app = Flask(__name__)

async def openlibrary_search(name, author):
    url = f'http://openlibrary.org/search.json?title={name}&author={author}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            json_response = await response.json()            
            if 'docs' in json_response and len(json_response['docs']) > 0:
                cover_id = json_response['docs'][0]['cover_i']
                return cover_id
            else:
                return None
    

async def search_books(prompt):
    responseFormat = "Please provide the recommendations in the following format: Each book should be on one line, and each line should only include three fields separated by '$': the book name, the book author, and a reason why each book is recommended, like this: Book name $ Book author $ A reason why this book is recommended. Please make sure not to include a number bullet in front of the book name."
    messages = [
        {"role": "user", "content" : f"You are an expert in books. You love to give book recommendations based on their needs. {responseFormat}"},
        {"role": "user", "content" : f"Generate books recommendations based on the user input: {prompt}. {responseFormat}"}
    ]
    response_data = openai_chat_completion("gpt-3.5-turbo", messages, 1024, 0.4)
    if not response_data:
        return {'error': 'OpenAI API call failed!'}

    book_lines = [line.strip() for line in response_data.split('\n') if line.strip()]

    async def process_book(line):
        # Split the line by the delimiter to extract book name and author
        book = line.split('$')
        # Ensure that the line has the expected number of parts (i.e., book name and author)
        if len(book) >= 3:
            name = book[0].strip()
            author = book[1].strip()
            description = book[2].strip()
            try:
                # Call openlibrary_search asynchronously to get cover ID
                cover_id_task = asyncio.create_task(openlibrary_search(name, author))
                # Wait for the cover ID to be retrieved
                cover_id = await cover_id_task
            except Exception as e:
                logger.warning(f'Failed to process book from openliarry: {name}, {author}. Error: {e}')
                cover_id = ""
            # Determine cover URL based on cover ID
            if not cover_id:
                cover_url = url_for('static', filename='no_cover.png')
            else:
                cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
            
            logger.info(f"Name: {name}, Author: {author}, ID: {cover_id}")
            return {'name': name, 'author': author, 'coverUrl': cover_url, 'description': description}
    
    # Create tasks to process each book in response_lines concurrently
    book_tasks = [asyncio.create_task(process_book(line)) for line in book_lines]
    # Wait for all book tasks to complete
    books = await asyncio.gather(*book_tasks)
    # Filter out None results
    return books




# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend')
def search():
    return render_template('search.html')

# AJAX call
@app.route('/search', methods=['POST'])
async def search_ajax_request():
    # Get the value of the 'prompt' parameter from the POST request
    prompt = request.form['prompt']
    # app.logger.info(prompt)
    if prompt:
        response_data = await search_books(prompt)
        if 'error' not in response_data:
            return jsonify({'books':response_data, 'userInput' : prompt})
        else:
            return jsonify(response_data)
    else:
        return jsonify({'error':'Missing prompt!'})

if __name__ == '__main__':
    app.run()

  

  

