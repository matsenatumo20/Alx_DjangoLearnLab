from django.db import models

# Create your models here.

# Author model represents an author with a name
class Author(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
# Book model represents a book with a title, publication year, and author
class Book(models.Model):
    title = models.CharField(max_length=200)
    publication_year = models.IntegerField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')

    def __str__(self):
        return self.title
