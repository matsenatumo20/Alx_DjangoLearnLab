from django.http import HttpResponse
from .models import Book

def list_books(request):
    books = Book.objects.all()
    
    if not books:
        return HttpResponse("No books found.")

    output = "Books in Database:\n\n"
    for book in books:
        output += f"- {book.title} by {book.author.name}\n"

    return HttpResponse(output, content_type="text/plain")


from django.shortcuts import render, get_object_or_404
from django.views.generic.detail import DetailView
from .models import Book, Library

# Function-Based View: List all books
def list_books(request):
    books = Book.objects.select_related('author').all()
    return render(request, 'relationship_app/list_books.html', {'books': books})

# Class-Based View: Library detail view with books
class LibraryDetailView(DetailView):
    model = Library
    template_name = 'relationship_app/library_detail.html'
    context_object_name = 'library'

