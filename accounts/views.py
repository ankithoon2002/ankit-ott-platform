from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from django.contrib import messages

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create a default profile
            UserProfile.objects.create(user=user, name=user.username)
            login(request, user)
            return redirect('select_profile')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('select_profile')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def select_profile(request):
    profiles = request.user.profiles.all()
    if request.method == 'POST':
        profile_id = request.POST.get('profile_id')
        if profile_id:
            request.session['active_profile_id'] = profile_id
            return redirect('home')
        
        # Adding a new profile
        name = request.POST.get('name')
        if name and profiles.count() < 4:
            avatar = request.POST.get('avatar', 'https://api.dicebear.com/7.x/avataaars/svg?seed=Felix')
            UserProfile.objects.create(user=request.user, name=name, avatar=avatar)
            return redirect('select_profile')

    return render(request, 'accounts/select_profile.html', {'profiles': profiles})
