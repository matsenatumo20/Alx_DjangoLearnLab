from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Profile


User = get_user_model()


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)


class Meta:
    model = User
    fields = ("username", "email", "first_name", "last_name", "password1", "password2")


def save(self, commit=True):
    user = super().save(commit=False)
    user.email = self.cleaned_data["email"]
    user.first_name = self.cleaned_data.get("first_name", "")
    user.last_name = self.cleaned_data.get("last_name", "")
    if commit:
        user.save()
    return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("bio", "avatar")

