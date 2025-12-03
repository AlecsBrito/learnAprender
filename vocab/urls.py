from django.urls import path
from . import views

app_name = 'vocab'

urlpatterns = [
    path('', views.VocabListView.as_view(), name='list'),
    path('add/', views.VocabCreateView.as_view(), name='add'),
    path('<int:pk>/', views.VocabDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.VocabUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.VocabDeleteView.as_view(), name='delete'),
    path('<int:pk>/generate/', views.generate_exercises_from_vocab, name='generate_exercises'),
    path('generate_all/', views.generate_exercises_from_all, name='generate_all_exercises'),
    path('generate_random/', views.generate_random_exercises, name='generate_random_exercises'),
]
