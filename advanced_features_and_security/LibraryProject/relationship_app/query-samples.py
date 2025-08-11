import os
import django

# Set up the Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
django.setup()

from relationship_app.models import Author, Book, Library, Librarian

def get_books_by_author(author_name):
    try:
        author = Author.objects.get(name=author_name)
        books = author.books.all()
        return books
    except Author.DoesNotExist:
        return None

def get_books_in_library(library_name):
    try:
        library = Library.objects.get(name=library_name)
        books = library.books.all()
        return books
    except Library.DoesNotExist:
        return None

def get_librarian_for_library(library_name):
    try:
        library = Library.objects.get(name=library_name)
        librarian = library.librarian
        return librarian
    except Library.DoesNotExist:
        return None

def main():
    # Create some sample data
    author1 = Author.objects.create(name='Author 1')
    book1 = Book.objects.create(title='Book 1', author=author1)
    book2 = Book.objects.create(title='Book 2', author=author1)

    library1 = Library.objects.create(name='Library 1')
    library1.books.add(book1, book2)

    librarian1 = Librarian.objects.create(name='Librarian 1', library=library1)

    # Query all books by a specific author
    books_by_author = get_books_by_author('Author 1')
    if books_by_author:
        print("Books by Author 1:")
        for book in books_by_author:
            print(book.title)
    else:
        print("Author not found.")

    # List all books in a library
    books_in_library = get_books_in_library('Library 1')
    if books_in_library:
        print("\nBooks in Library 1:")
        for book in books_in_library:
            print(book.title)
    else:
        print("Library not found.")

    # Retrieve the librarian for a library
    librarian = get_librarian_for_library('Library 1')
    if librarian:
        print(f"\nLibrarian for Library 1: {librarian.name}")
    else:
        print("Library not found.")

if __name__ == '__main__':
    main()
