from django.urls import path
from . import views

app_name = 'exercises'

urlpatterns = [
    path('', views.ExerciseListView.as_view(), name='list'),
    path('add/', views.create_exercise, name='create'),
    path('<int:pk>/', views.ExerciseDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.edit_exercise, name='edit'),
    path('<int:pk>/delete/', views.delete_exercise, name='delete'),
    path('<int:pk>/take/', views.take_exercise, name='take'),
]
