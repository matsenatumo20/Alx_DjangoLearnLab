# Update Operation

## Command
book = Book.objects.get(title='1984")
book.title = "Nineteen Eighty-Four"
book.save()
book = Book.objects.get(title="Nineteen Eighty-Four")
print(book.title)


*Output*
Nineteen Eighty-Four

