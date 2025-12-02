from django.urls import path
from . import views

app_name = 'reviews'
urlpatterns = [
    path('', views.index, name='index'),
    path('progress/', views.progress, name='progress'),
    path('high-error-words/', views.high_error_words, name='high_error_words'),
    path('schedule/<int:vocab_id>/', views.schedule_review, name='schedule_review'),
    path('scheduled/', views.scheduled_reviews, name='scheduled_reviews'),
]
