# Define a custom user model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.conf import settings


class CustomUserManager(BaseUserManager):
    # Method to create a new user
    def create_user(self, username, email=None, password=None, **extra_fields):
        # Set default values for is_staff and is_superuser
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    # Method to create a new superuser
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        # Set default values for is_staff and is_superuser
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        # Check if is_staff and is_superuser are True
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(username, email, password, **extra_fields)

    # Private method to create a new user
    def _create_user(self, username, email, password, **extra_fields):
        # Check if username is provided
        if not username:
            raise ValueError('The given username must be set')
        # Normalize the email
        email = self.normalize_email(email)
        # Create a new user
        user = self.model(username=username, email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


# Define the custom user model
class CustomUser(AbstractUser):
    date_of_birth = models.DateField(null=True, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    objects = CustomUserManager()

# Define the Book model
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    publication_year = models.IntegerField()

# Define custom permissions for the Book model
    class Meta:
        permissions = [
            ("can_view", "Can view book"),
            ("can_create", "Can create book"),
            ("can_edit", "Can edit book"),
            ("can_delete", "Can delete book"),
        ]

    def __str__(self):
        return self.title


class MyModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Define custom permissions for the Book model
    class Meta:
        permissions = [
            ("can_view", "Can view book"),
            ("can_create", "Can create book"),
            ("can_edit", "Can edit book"),
            ("can_delete", "Can delete book"),
        ]

    def __str__(self):
        return self.title


