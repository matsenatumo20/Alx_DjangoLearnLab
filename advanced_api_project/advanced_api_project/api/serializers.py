from rest_framework import serializers
from .models import Book
from .models import Author
from datetime import date

# BookSerializer serializes all fields of the Book model with custom validation to ensure publication year is not in the future
class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

    def validate_publication_year(self, value):
        if value > date.today().year:
            raise serializers.ValidationError('Publication year cannot be in the future')
        return value

# AuthorSerializer serializes the Author model with nested BookSerializer to dynamically serialize related books
class AuthorSerializer(serializers.ModelSerializer):
    books = BookSerializer(many=True, read_only=True)

    class Meta:
        model = Author
        fields = ['id', 'name', 'books']
