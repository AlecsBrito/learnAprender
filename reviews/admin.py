from django.contrib import admin
from .models import ReviewSchedule


@admin.register(ReviewSchedule)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'vocabulary', 'scheduled_at', 'error_count')
    list_filter = ('scheduled_at',)
