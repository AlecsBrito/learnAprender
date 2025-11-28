from django import forms
from .models import Vocabulary


class VocabularyForm(forms.ModelForm):
    class Meta:
        model = Vocabulary
        fields = ['word', 'translation', 'example', 'category', 'level', 'tags']
