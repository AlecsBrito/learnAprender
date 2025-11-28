from django.db import models
from django.contrib.auth.models import User


class ReviewSchedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vocabulary = models.ForeignKey('vocab.Vocabulary', on_delete=models.CASCADE)
    scheduled_at = models.DateTimeField()
    error_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Revisão {self.vocabulary} para {self.user.username} em {self.scheduled_at}"
