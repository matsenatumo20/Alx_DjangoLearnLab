from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author']  # add fields you need

class BookSearchForm(forms.Form):
    q = forms.CharField(max_length=200, required=False)

    def clean_q(self):
        q = self.cleaned_data.get('q', '')
        # optional additional validation/sanitization here
        return q

