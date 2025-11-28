from django.contrib import admin
from .models import Quiz, QuizResult


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'theme', 'created_by')
    search_fields = ('title', 'theme')


@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'taken_at')
