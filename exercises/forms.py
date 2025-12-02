from django import forms
from .models import Exercise
import json


class ExerciseForm(forms.ModelForm):
    choices_text = forms.CharField(
        label='Opções (para Múltipla Escolha)',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Digite cada opção em uma nova linha. Ex:\nopção 1\nopção 2\nopção 3'
        }),
        help_text='Para exercícios de múltipla escolha, digite cada opção em uma nova linha.'
    )
    
    class Meta:
        model = Exercise
        fields = ['question', 'exercise_type', 'answer', 'level', 'category', 'is_shared']
        widgets = {
            'question': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Digite a pergunta ou instrução'
            }),
            'exercise_type': forms.Select(attrs={'class': 'form-select'}),
            'answer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite a resposta correta'
            }),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Verbos, Vocabulário, Phrasal Verbs'
            }),
            'is_shared': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.choices:
            self.fields['choices_text'].initial = '\n'.join(self.instance.choices)
        
        # Add level choices dynamically
        self.fields['level'].choices = [
            ('', '--- Selecionar Nível ---'),
            ('beginner', 'Iniciante'),
            ('intermediate', 'Intermediário'),
            ('advanced', 'Avançado'),
        ]
    
    def clean(self):
        cleaned_data = super().clean()
        exercise_type = cleaned_data.get('exercise_type')
        choices_text = cleaned_data.get('choices_text', '').strip()
        
        if exercise_type == 'mcq' and not choices_text:
            raise forms.ValidationError('Múltipla escolha requer opções.')
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        choices_text = self.cleaned_data.get('choices_text', '').strip()
        
        if choices_text:
            instance.choices = [c.strip() for c in choices_text.split('\n') if c.strip()]
        else:
            instance.choices = None
        
        if commit:
            instance.save()
        return instance
