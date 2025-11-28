from django.contrib import admin
from .models import Exercise, PerformanceRecord


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('question', 'exercise_type', 'level', 'category', 'created_by')
    search_fields = ('question',)


@admin.register(PerformanceRecord)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'exercise', 'correct', 'timestamp')
    list_filter = ('correct',)
