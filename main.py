from flask_app import app, logger
from flask import render_template, request, jsonify, url_for, session, send_from_directory
import uuid # for generate user_session_id
import asyncio # for running API calls concurrently
from api.openai_api import openai_chat_completion
from api.openlibrary_api import openlibrary_search
from datastore.redis_conn import RedisClient

# Create the Redis Connection for storing books for each user session
redis_client = RedisClient()

def prompt_engineer(user_prompt, user_session_id, prompt_type = 0):
    responseFormat = "Provide recommendations in the following format: Each book should be on one line, and each line should only include three fields separated by '$': the book name, author, and a reason why it is recommended, like this: Book name$Book author$A reason why this book is recommended. Make sure not to include a number bullet in front of the book name and don't recommend a book that has been recommended before."
    messages = [
        {"role": "user", "content" : f"You are an expert in books. You role is to give book recommendations based on their needs. {responseFormat}"}
    ]
    if prompt_type == "search": # book recommendation
        user_input_message = {"role": "user", "content" : f"Generate at least 6 book recommendations based on the user input: {user_prompt}. {responseFormat}"}
        messages.append(user_input_message)
    elif prompt_type == "more": # more book recommendation
        history_user_mesage = {"role": "user", "content" : f"Generate book recommendations based on the user input: {user_prompt}."}
        history_books = redis_client.get_books(user_session_id)
        history_books_string = ', '.join(str(elem) for elem in history_books)
        #logger.debug(f"books have been recommended: {history_books_string}")
        history_ui_message = {"role": "assistant", "content" : f"{history_books_string}"}
        messages.append(history_user_mesage)
        messages.append(history_ui_message)
        user_input_message = {"role": "user", "content" : f"Generate at least 6 more book recommendations. {responseFormat}"}
        messages.append(user_input_message)
    return messages

async def search_books(messages, user_session_id):
    
    #!!may need to change later to handle errors here: https://github.com/openai/openai-cookbook/blob/main/examples/How_to_handle_rate_limits.ipynb
    response_data = openai_chat_completion(messages, "gpt-3.5-turbo", 1024, 0.4)
    if not response_data: 
        return {'error': 'OpenAI API call failed!'}
    
    
    # process books from OpenAI
    book_lines = [line.strip() for line in response_data.split('\n') if line.strip()]
    logger.info(f"OpenAI API returned {len(book_lines)} books.")
    async def process_book(line):
        # Split the line by the delimiter to extract book name and author
        book = line.split('$')
        # Ensure that the line has the expected number of parts (i.e., book name and author)
        if len(book) >= 3:
            name = book[0].strip()
            author = book[1].strip()
            description = book[2].strip()

            # Call openlibrary_search asynchronously to get cover ID
            # base on cover ID, it will generate cover url
            try:
                cover_id_task = asyncio.create_task(openlibrary_search(name, author))
                # Wait for the cover ID to be retrieved
                cover_id = await cover_id_task
            except Exception as e:
                logger.warning(f'Openlibrary API: Failed to process book {name}, {author}. Error: {e}')
                cover_id = ""

            # Determine cover URL based on cover ID
            if not cover_id:
                cover_url = url_for('static', filename='no_cover.png')
            else:
                cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
            
            logger.debug(f"Books: Name: {name}, Author: {author}, ID: {cover_id}")
            # add the book to redis
            if redis_client.add_book(user_session_id, name) == 0:
                logger.error(f"Redis: failed to add one book to the user: {name}, {author}")
            else:
                return {'name': name, 'author': author, 'coverUrl': cover_url, 'description': description}
    
    # Create tasks to process each book in response_lines concurrently
    book_tasks = [asyncio.create_task(process_book(line)) for line in book_lines]
    # Wait for all book tasks to complete
    books = await asyncio.gather(*book_tasks)
    return books

@app.before_request
def check_session():
    if session.get("user_id") is None:
        session['user_id'] = str(uuid.uuid4())
        logger.info(f"new user: {session['user_id']}")

@app.route('/')
def home():
    # index.html is a static file, it can be served directly from the file system without any processing (Jinja2), 
    # which makes send_from_directory the faster option.
    #return render_template('index.html')
    return send_from_directory('templates', 'index.html')

@app.route('/about')
def about():
    #return render_template('about.html')
    return send_from_directory('templates', 'about.html')

@app.route('/recommend')
def search():
    #return render_template('search.html')
    return send_from_directory('templates', 'search.html')

# AJAX call: search for books
@app.route('/search', methods=['POST'])
async def search_request():
    # Get the value of the 'prompt' parameter from the POST request
    prompt = request.form['prompt']
    action = request.form['action']
    if prompt:
        user_session_id = f"{session['user_id']}-{prompt}"
        if redis_client.check_connection():
            if action == "search" and redis_client.is_user_session_exist(user_session_id):
                #new book search: remove the previous books
                redis_client.remove_user_session(user_session_id)
            
            if action == "more" and redis_client.get_num_books(user_session_id) <= 0:
                response_data = {'error':'Session expired. Cannot get more books!'}
            else:
                #sent request to ChatGPT and openlibary and store the list of books in redis session
                messages = prompt_engineer(prompt, user_session_id, action)
                response_data = await search_books(messages, user_session_id)
                logger.info(f"added {len(response_data)} books to Redis")
                #set expiry seconds for the redis session (default: 1 hour)
                redis_client.expire_user_session_after(user_session_id)
        else:
            response_data = {'error':'Cannot connect to redis!'}
    else:
        response_data = {'error':'Missing prompt!'}

    if 'error' not in response_data:
        return jsonify({'books':response_data, 'userInput' : prompt})
    else:
        return jsonify(response_data)

"""
@app.errorhandler(400)
def handle_bad_request(e):
    return "Bad request", 400

@app.errorhandler(500)
def handle_server_error(e):
    return "Server error", 500
"""  



if __name__ == '__main__':
    app.run()