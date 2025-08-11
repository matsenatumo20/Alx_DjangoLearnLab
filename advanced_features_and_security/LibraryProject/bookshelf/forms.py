# LibraryProject/bookshelf/forms.py
from django import forms
from .models import Book  # assuming you have a Book model

class ExampleForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'description']  # adjust to your model fields

    # Extra validation example to avoid unsafe input
    def clean_title(self):
        title = self.cleaned_data.get('title', '')
        if "<script>" in title.lower():
            raise forms.ValidationError("Invalid input detected.")
        return title


