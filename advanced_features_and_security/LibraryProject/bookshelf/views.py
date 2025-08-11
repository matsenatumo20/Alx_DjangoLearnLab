# Import the permission_required decorator to check for permissions
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, redirect
from .models import Book
from .forms import BookForm

# Use the permission_required decorator to check if the user has the 'can_view' permission
# If the user doesn't have the permission, a 403 Forbidden response will be returned
@permission_required('library.can_view', raise_exception=True)
def book_list(request):
    # View code to list books
    books = Book.objects.all()
    return render(request, 'book_list.html', {'books': books})

# Use the permission_required decorator to check if the user has the 'can_create' permission
@permission_required('library.can_create', raise_exception=True)
def create_book(request):
    # View code to create a new book
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'create_book.html', {'form': form})

# Use the permission_required decorator to check if the user has the 'can_edit' permission
@permission_required('library.can_edit', raise_exception=True)
def edit_book(request, pk):
    # View code to edit a book
    book = Book.objects.get(pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'edit_book.html', {'form': form})

# Use the permission_required decorator to check if the user has the 'can_delete' permission
@permission_required('library.can_delete', raise_exception=True)
def delete_book(request, pk):
    # View code to delete a book
    book = Book.objects.get(pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')
    return render(request, 'delete_book.html', {'book': book})



