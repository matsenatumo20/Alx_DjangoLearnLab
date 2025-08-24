from django.urls import path
from .views import AuthLoginView, AuthLogoutView, RegisterView, ProfileView


app_name = 'blog'

urlpatterns = [
    path('login', AuthLoginView.as_view(), name='login'),
    path('logout', AuthLogoutView.as_view(), name='logout'),
    path('register', RegisterView.as_view(), name='register'),
    path('profile', ProfileView.as_view(), name='profile'),
]
