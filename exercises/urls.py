from django.urls import path
from . import views

app_name = 'exercises'

urlpatterns = [
    path('', views.ExerciseListView.as_view(), name='list'),
    path('<int:pk>/', views.ExerciseDetailView.as_view(), name='detail'),
    path('<int:pk>/take/', views.take_exercise, name='take'),
]
