from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=False)
    level = forms.ChoiceField(choices=(('beginner','Iniciante'),('intermediate','Intermediário')),
                              required=False)
    objectives = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class ProfileUpdateForm(forms.ModelForm):
    """Form to update user profile information."""
    class Meta:
        model = Profile
        fields = ('level', 'objectives')
        widgets = {
            'level': forms.Select(attrs={'class': 'form-select'}),
            'objectives': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'level': 'Nível de Conhecimento',
            'objectives': 'Objetivos de Aprendizado',
        }
