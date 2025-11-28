from django.db import models
from django.contrib.auth.models import User


class Vocabulary(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'Iniciante'),
        ('intermediate', 'Intermediário'),
    ]
    word = models.CharField(max_length=200)
    translation = models.CharField(max_length=400)
    example = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    tags = models.CharField(max_length=200, blank=True, help_text='Use vírgulas para separar')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.word
