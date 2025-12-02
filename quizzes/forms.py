from django import forms
from .models import Quiz


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'level', 'theme', 'is_shared']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título do quiz'}),
            'level': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: iniciante, intermediário, avançado'}),
            'theme': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: food, travel, business'}),
            'is_shared': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
