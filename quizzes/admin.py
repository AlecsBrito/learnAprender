from django.contrib import admin
from .models import Quiz, QuizResult


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'theme', 'created_by', 'is_shared', 'created_at')
    list_filter = ('is_shared', 'level', 'theme', 'created_at')
    search_fields = ('title', 'theme')
    readonly_fields = ('created_at',)


@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'taken_at')
    list_filter = ('score', 'taken_at')
    search_fields = ('user__username', 'quiz__title')
    readonly_fields = ('taken_at',)
