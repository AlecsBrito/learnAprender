from django.urls import path
from . import views

app_name = 'quizzes'

urlpatterns = [
    path('', views.index, name='index'),
    path('generate/', views.generate_quiz, name='generate'),
    path('<int:quiz_id>/take/', views.take_quiz, name='take'),
    path('<int:result_id>/result/', views.quiz_result, name='result'),
]
