from flask_app import app, logger
from flask import render_template, request, jsonify, url_for, session, send_from_directory

import uuid # for generate user_session_id
import asyncio # for running API calls concurrently

from api.openai_api import openai_chat_completion
from api.openlibrary_api import openlibrary_search

from memory.memory import Memory
from memory.cache import Cache
from datastore.redis_datastore import RedisDataStore


# Create the Redis Connection for storing books for each user session
redis_datastore = RedisDataStore()
memory = Memory(redis_datastore)
cache = Cache(redis_datastore)

def prompt_engineer(user_prompt, user_session_id, prompt_type = 0):

    if prompt_type == "search": # book recommendation
        history_books_string = ''
    elif prompt_type == "more": # more book recommendation
        history_books = cache.get_books(user_session_id)
        history_books_string = ', '.join(str(elem) for elem in history_books)
    
    prompt = f"""
As an expert in books, your role is to provide book recommendations. Please follow the instructions below carefully:

You will be provided with the user's input delimited by <>, and a list of previously recommended books delimited by ```.
Your task is to provide the BEST book recommendations, by following these steps:
Step 1 - Analyze the user's input to understand their specific needs and interests, such as their preferred genre, subject, theme, writing style, or author.
Step 2 - Base on the user's needs and interests, conduct research and look for books with positive reviews, high ratings. If the user's input specifies the age or reading level, consider books that are appropriate for the age or reading level.
Step 3 - Generate a list of books that fits the user's needs and interests.
Step 4 - Compare your list of books with the list of previously recommended books. If any books in your list are also in the list of previously recommended books, remove them from your list and find new books to recommend. Repeat this step until you have a list of at least 6 books that fits the user's needs and interests and have not been previously recommended. If you cannot find any books to recommend, simply return empty string.

Your response should ONLY have the list of books. Do NOT include any additional text.
And the list of books returned should be formatted as follows:
- Each book should be on a separate line
- Each line should start with the book's name, followed by a '$' sign, then the author's name, followed by another '$' sign, and then the reasons why the book is recommended. Like this: Book name$author$Reasons why this book is recommended.
- Do not include any additional text or formatting in front of book names.
- If you cannot find any books to recommend, simply return empty string.

List of previously recommended books: ```{history_books_string}```

User's input: <{user_prompt}>
    """

    logger.debug(prompt)

    messages = [
        {"role": "system", "content" : "You are an expert in books. You role is to give book recommendations based on users' needs and interests."},
        {"role": "user", "content" : prompt}
    ]
    return messages

async def search_books(messages, user_session_id):
    
    #!!may need to change later to handle errors here: https://github.com/openai/openai-cookbook/blob/main/examples/How_to_handle_rate_limits.ipynb
    response_data = openai_chat_completion(messages, "gpt-3.5-turbo", 1024, 0.2)
    if not response_data: 
        return {'error': 'OpenAI API call failed!'}
    
    
    # process books from OpenAI
    book_lines = [line.strip() for line in response_data.split('\n') if line.strip()]
    logger.info(book_lines)
    #logger.info(f"OpenAI API returned {len(book_lines)} books: {book_lines}")
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
            if cache.add_book(user_session_id, name) == 0:
                logger.error(f"Redis: failed to add one book to the user: {name}, {author}")
            else:
                return {'name': name, 'author': author, 'coverUrl': cover_url, 'description': description}
        else:
            logger.error(f"cannot process this book from OpenAI: {book}")
    
    # Create tasks to process each book in response_lines concurrently
    book_tasks = [asyncio.create_task(process_book(line)) for line in book_lines]
    # Wait for all book tasks to complete
    books = await asyncio.gather(*book_tasks)
    # filter out None book in the books
    return [item for item in books if item is not None]

@app.before_request
def check_session():
    if session.get("user_id") is None:
        session['user_id'] = str(uuid.uuid4())
        logger.info(f"new user: {session['user_id']}")

@app.route('/')
def home():
    # index.html is a static file, it can be served directly from the file system without any processing (Jinja2), 
    # which makes send_from_directory the faster option.
    return render_template('index.html')
    #return send_from_directory('templates', 'index.html')

@app.route('/about')
def about():
    #return render_template('about.html')
    return send_from_directory('templates', 'about.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form['userMessage']
    #return render_template('about.html')
    ai_response = "ok"
    return jsonify({'ai_response':ai_response})

@app.route('/recommend')
def search():
    return render_template('search.html')
    #return send_from_directory('templates', 'search.html')


# AJAX call: search for books
@app.route('/search', methods=['POST'])
async def search_request():
    # Get the value of the 'prompt' parameter from the POST request
    prompt = request.form['prompt']
    action = request.form['action']

    if prompt:
        user_books_cache_id = f"{session['user_id']}-{prompt}"
        if cache.check_connection():
            if action == "search" and cache.is_user_cache_exist(user_books_cache_id):
                #new book search: remove the previous books
                cache.remove_user_cache(user_books_cache_id)
            
            if action == "more" and cache.get_num_books(user_books_cache_id) <= 0:
                response_data = {'error':'Session expired. Failed to get more books!'}
            else:
                #sent request to ChatGPT and openlibary and store the list of books in redis session
                messages = prompt_engineer(prompt, user_books_cache_id, action)
                response_data = await search_books(messages, user_books_cache_id)
                if len(response_data) <= 0:
                    response_data = {'error':'Receive empty recommendations from ChatGPT'}
                else:
                    #set expiry seconds for the redis session (default: 1 hour)
                    cache.expire_user_cache_after(user_books_cache_id)
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