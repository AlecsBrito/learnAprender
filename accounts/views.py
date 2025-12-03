from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import SignUpForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'accounts/home.html')


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # save profile extra fields
            level = form.cleaned_data.get('level')
            objectives = form.cleaned_data.get('objectives')
            if level or objectives:
                profile = user.profile
                if level:
                    profile.level = level
                if objectives:
                    profile.objectives = objectives
                profile.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user.profile)
    
    return render(request, 'accounts/profile.html', {'form': form})
