from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from django.contrib.auth.models import User
from django.contrib import messages



# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You have been registered successfully!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'blog/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You have been logged in successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'blog/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('home')

@login_required
def profile(request):
    user = request.user
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            user.email = email
            user.save()
            messages.success(request, 'Your profile has been updated successfully!')
        else:
            messages.error(request, 'Email is required.')
        return redirect('profile')
    return render(request, 'blog/profile.html', {'user': user})


