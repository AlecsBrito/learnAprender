from django import forms
from .models import Quiz


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'level', 'theme', 'is_shared']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'level': forms.TextInput(attrs={'class': 'form-control'}),
            'theme': forms.TextInput(attrs={'class': 'form-control'}),
            'is_shared': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
