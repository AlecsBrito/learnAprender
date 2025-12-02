from django.db import models
from django.contrib.auth.models import User


class Quiz(models.Model):
    title = models.CharField(max_length=200)
    level = models.CharField(max_length=50, blank=True)
    theme = models.CharField(max_length=100, blank=True)
    questions = models.ManyToManyField('exercises.Exercise', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_shared = models.BooleanField(default=False, help_text='Se marcado, quiz é disponível para todos os usuários')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        shared_str = ' (compartilhado)' if self.is_shared else ''
        return f"{self.title}{shared_str}"


class QuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField()
    taken_at = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['-taken_at']
