from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignUpForm
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
    return render(request, 'accounts/profile.html')
