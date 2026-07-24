"""Check WeRead shelf data including albums."""
import sys
sys.path.insert(0, '.')

from app.core.config import settings
from app.services.weread_client import WeReadClient
import asyncio

async def main():
    client = WeReadClient(settings.WEREAD_API_KEY)
    try:
        shelf_data = await client.get_shelf()
        books = shelf_data.get('books', [])
        albums = shelf_data.get('albums', [])
        mp = shelf_data.get('mp', None)
        
        print(f'Books: {len(books)}')
        print(f'Albums: {len(albums)}')
        print(f'MP: {"Yes" if mp else "No"}')
        print(f'Total shelf items: {len(books) + len(albums) + (1 if mp else 0)}')
        
        if albums:
            print('\nSample albums:')
            for i, album in enumerate(albums[:5]):
                album_info = album.get('albumInfo', {})
                print(f'{i+1}. {album_info.get("name", "N/A")} - {album_info.get("authorName", "N/A")}')
        
        if books:
            print('\nSample books:')
            for i, book in enumerate(books[:5]):
                print(f'{i+1}. {book.get("title", "N/A")} - {book.get("author", "N/A")}')
                
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())