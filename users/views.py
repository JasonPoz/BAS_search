from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import User
from .forms import UserForm, CustomUserCreationForm
from django.contrib.auth import login


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dictionary:home')
    else:
        form = CustomUserCreationForm()
    return render(request,"registration/registration_form.html",{'form':form})

@login_required
def profile(request, username):
    profile = get_object_or_404(User, username=username)
    context = {'profile': profile}
    return render(request, 'users/profile.html', context)

@login_required
def edit_profile(request):
    profile = get_object_or_404(
        User,
        username = request.user)
    form = UserForm(request.POST or None, instance=profile)
    if form.is_valid():
        form.save()
        return redirect('users:profile', request.user)
    context = {'form': form}
    return render(request, 'users/form_edit_profile.html', context)