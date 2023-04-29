from config import app, logger
from flask import render_template, request, jsonify, url_for, session
import uuid # for generate user_session_id
import asyncio # for running API calls concurrently
from api.openai_api import openai_chat_completion
from api.openlibrary_api import openlibrary_search
from datastore.RedisConn import RedisClient

# Create the Redis Connection for storing books for each user session
redis_client = RedisClient()

async def search_books(prompt, user_session_id):
    responseFormat = "Please provide the recommendations in the following format: Each book should be on one line, and each line should only include three fields separated by '$': the book name, the book author, and a reason why each book is recommended, like this: Book name $ Book author $ A reason why this book is recommended. Please make sure not to include a number bullet in front of the book name."
    messages = [
        {"role": "user", "content" : f"You are an expert in books. You love to give book recommendations based on their needs. {responseFormat}"},
        {"role": "user", "content" : f"Generate books recommendations based on the user input: {prompt}. {responseFormat}"}
    ]
    #!!may need to change later to handle errors here: https://github.com/openai/openai-cookbook/blob/main/examples/How_to_handle_rate_limits.ipynb
    response_data = openai_chat_completion(messages, "gpt-3.5-turbo", 1024, 0.4)
    if not response_data: 
        return {'error': 'OpenAI API call failed!'}
    
    # process books from OpenAI
    book_lines = [line.strip() for line in response_data.split('\n') if line.strip()]
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
            
            logger.info(f"Books: Name: {name}, Author: {author}, ID: {cover_id}")
            # add the book to redis
            if redis_client.add_book(user_session_id, name) == 0:
                logger.error(f"Redis: failed to add one book to the user set: {name}, {author}")
            
            return {'name': name, 'author': author, 'coverUrl': cover_url, 'description': description}
    
    # Create tasks to process each book in response_lines concurrently
    book_tasks = [asyncio.create_task(process_book(line)) for line in book_lines]
    # Wait for all book tasks to complete
    books = await asyncio.gather(*book_tasks)
    return books



# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route('/')
def home():
    if session.get("user_session_id") is None:
        session['user_session_id'] = str(uuid.uuid4())
        logger.info(f"Flask_OpenAI: home page: new user {session['user_session_id']}")
    return render_template('index.html')

@app.route('/recommend')
def search():
    if session.get("user_session_id") is None:
        session['user_session_id'] = str(uuid.uuid4())
        logger.info(f"Flask_OpenAI: recommend redirect: couldnt find user id, created a new one: {session['user_session_id']}")
    return render_template('search.html')

# AJAX call
@app.route('/search', methods=['POST'])
async def search_request():
    # Get the value of the 'prompt' parameter from the POST request
    prompt = request.form['prompt']
    user_session_id = session['user_session_id']
    
    if prompt:
        if redis_client.check_connection():
            #new book search: remove the previous books
            redis_client.remove_user(user_session_id)
            #sent request to ChatGPT and openlibary and store the list of books in redis session
            response_data = await search_books(prompt, user_session_id)
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


if __name__ == '__main__':
    app.run()

  

  

