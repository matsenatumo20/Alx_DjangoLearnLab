# Create Operation

## Command
python
from bookshelf.models import Book
book = Book(title="1984", author="George Orwell", published_date=1949)
book.save()


*Output*
No output is displayed when creating a book instance.

# Retrieve Operation

## Command
python
book = Book.objects.get(title="1984")
print(book.title, book.author, book.published_date)

*Output*
1984 George Orwell 1949

# Update Operation

## Command
python
book = Book.objects.get(title='1984")
book.title = "Nineteen Eighty-Four"
book.save()
book = Book.objects.get(title="Nineteen Eighty-Four")
print(book.title)


*Output*
Nineteen Eighty-Four

# Delete a book

## Command
python
book = Book.objects.get(title="Nineteen Eighty-Four")
book.delete()
print(Book.objects.all()


*Output*)
<QuerySet []>