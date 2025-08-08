# relationship_app/query_samples.py

import os
import django

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LibraryProject.settings')
django.setup()

from relationship_app.models import Author, Book, Library, Librarian

def query_books_by_author(author_name):
    print(f"\nBooks by author: {author_name}")
    try:
        author = Author.objects.get(name=author_name)
        books = Book.objects.filter(author=author)
        for book in books:
            print(f"- {book.title}")
    except Author.DoesNotExist:
        print("Author not found.")

def list_books_in_library(library_name):
    print(f"\nBooks in library: {library_name}")
    try:
        library = Library.objects.get(name=library_name)
        books = library.books.all()
        for book in books:
            print(f"- {book.title}")
    except Library.DoesNotExist:
        print("Library not found.")

def get_librarian_for_library(library_name):
    print(f"\nLibrarian for library: {library_name}")
    try:
        library = Library.objects.get(name=library_name)
        librarian = Librarian.objects.get(library=library)
        print(f"Librarian: {librarian.name}")
    except Library.DoesNotExist:
        print("Library not found.")
    except Librarian.DoesNotExist:
        print("No librarian assigned to this library.")

if __name__ == "__main__":
    # Replace these names with values present in your DB
    query_books_by_author("J.K. Rowling")
    list_books_in_library("City Library")
    get_librarian_for_library("City Library")
