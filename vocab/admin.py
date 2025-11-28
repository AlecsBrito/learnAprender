from django.contrib import admin
from .models import Vocabulary


@admin.register(Vocabulary)
class VocabularyAdmin(admin.ModelAdmin):
    list_display = ('word', 'translation', 'category', 'level', 'created_by')
    search_fields = ('word', 'translation', 'tags')
    list_filter = ('level', 'category')
