from django.shortcuts import render
from .models import Book

def list_books(request):
    books = Book.objects.all()

    context = {'books: books'}
    return render(request, 'books/list_books.html', context)

from django.views.generic import DetailView
from .models import Library

class LibraryDetailView(DetailView):
    model = Library
    template_name = 'books/library_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['books'] = self.object.books.all()
        return context


