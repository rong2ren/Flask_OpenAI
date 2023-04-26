
import requests

def openlibary_search(bookName, author):
  # Fetch book information results from Open Library API
  url = f'https://openlibrary.org/search.json?author={author}&q={bookName}'
  
  openLibraryResponse = requests.get(url)
  if openLibraryResponse.status_code != 200:
    print(f'Failed to fetch books from Open Library API: {openLibraryResponse.status_code} {openLibraryResponse.data}')
    return None
  
  openLibraryData = openLibraryResponse.json()
  if openLibraryData['numFound'] == 0 or len(openLibraryData['docs']) == 0:
    print("Cannot find book " + bookName + " on OpenLibary")
    return None
  
  for book in openLibraryData['docs']:
    if 'cover_i' in book:
      return book['cover_i']
    
  return None