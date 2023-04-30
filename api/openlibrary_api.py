import requests
from flask_app import logger # for logging
import aiohttp

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

def openlibary_search_2(bookName, author):
  # Fetch book information results from Open Library API
  url = f'https://openlibrary.org/search.json?author={author}&q={bookName}'
  
  openLibraryResponse = requests.get(url)
  if openLibraryResponse.status_code != 200:
    logger.error(f'OpenLibary: Failed to fetch books from Open Library API: {openLibraryResponse.status_code} {openLibraryResponse.data}')
    return None
  
  openLibraryData = openLibraryResponse.json()
  if openLibraryData['numFound'] == 0 or len(openLibraryData['docs']) == 0:
    logger.error("OpenLibary: Cannot find book " + bookName + " on OpenLibary")
    return None
  
  for book in openLibraryData['docs']:
    if 'cover_i' in book:
      return book['cover_i']
    
  return None