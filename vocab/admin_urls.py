from django.urls import path
from . import admin_views

app_name = 'panel'

urlpatterns = [
    path('vocab/', admin_views.vocab_list_admin, name='vocab_list'),
    path('vocab/add/', admin_views.vocab_create_admin, name='vocab_add'),
    path('vocab/<int:pk>/edit/', admin_views.vocab_edit_admin, name='vocab_edit'),
    path('vocab/<int:pk>/delete/', admin_views.vocab_delete_admin, name='vocab_delete'),
    path('vocab/<int:pk>/generate/', admin_views.vocab_generate_exercises_admin, name='vocab_generate'),
]
