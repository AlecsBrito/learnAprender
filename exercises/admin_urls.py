from django.urls import path
from . import admin_views

app_name = 'panel_exercises'

urlpatterns = [
    path('', admin_views.exercise_list_admin, name='exercise_list'),
    path('add/', admin_views.exercise_create_admin, name='exercise_add'),
    path('<int:pk>/edit/', admin_views.exercise_edit_admin, name='exercise_edit'),
    path('<int:pk>/delete/', admin_views.exercise_delete_admin, name='exercise_delete'),
]
