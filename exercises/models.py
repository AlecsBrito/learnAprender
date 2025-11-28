from django.db import models
from django.contrib.auth.models import User


class Exercise(models.Model):
    TYPE_CHOICES = [
        ('mcq', 'Múltipla escolha'),
        ('gap', 'Preencher lacuna'),
        ('translate', 'Tradução'),
    ]
    question = models.TextField()
    exercise_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    choices = models.JSONField(blank=True, null=True, help_text='Lista de escolhas para MCQ')
    answer = models.TextField()
    level = models.CharField(max_length=20, blank=True)
    category = models.CharField(max_length=100, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_exercise_type_display()} - {self.question[:40]}"


class PerformanceRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    correct = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
