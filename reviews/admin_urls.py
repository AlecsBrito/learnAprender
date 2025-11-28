from django.urls import path
from . import admin_views

app_name = 'panel_metrics'

urlpatterns = [
    path('dashboard/', admin_views.metrics_dashboard, name='dashboard'),
    path('user/<int:user_id>/', admin_views.user_performance, name='user_performance'),
    path('records/', admin_views.performance_records, name='records'),
    path('quizzes/', admin_views.quiz_results_view, name='quizzes'),
]
