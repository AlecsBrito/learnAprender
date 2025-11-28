from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from exercises.models import PerformanceRecord
from quizzes.models import QuizResult
from django.db.models import Count, Q, F, Sum
from django.db.models.functions import Cast
from django.db.models import FloatField, Case, When
from django.utils import timezone
from datetime import timedelta


@staff_member_required
def metrics_dashboard(request):
    """Show overall performance metrics and user statistics."""
    users_with_performance = User.objects.annotate(
        num_attempts=Count('performancerecord')
    ).filter(num_attempts__gt=0).order_by('-num_attempts')[:20]

    total_attempts = PerformanceRecord.objects.count()
    total_correct = PerformanceRecord.objects.filter(correct=True).count()
    overall_accuracy = (total_correct / total_attempts * 100) if total_attempts > 0 else 0

    total_quizzes_taken = QuizResult.objects.count()
    avg_quiz_score = QuizResult.objects.aggregate(avg=Sum('score') / Count('id'))['avg'] or 0

    context = {
        'users_with_performance': users_with_performance,
        'total_attempts': total_attempts,
        'total_correct': total_correct,
        'overall_accuracy': round(overall_accuracy, 2),
        'total_quizzes_taken': total_quizzes_taken,
        'avg_quiz_score': round(avg_quiz_score, 2),
    }
    return render(request, 'panel/metrics_dashboard.html', context)


@staff_member_required
def user_performance(request, user_id):
    """Show detailed performance metrics for a specific user."""
    user = get_object_or_404(User, pk=user_id)

    # Exercise performance
    perf = PerformanceRecord.objects.filter(user=user)
    total = perf.count()
    correct = perf.filter(correct=True).count()
    accuracy = (correct / total * 100) if total > 0 else 0

    # Recent activity (last 7 days)
    week_ago = timezone.now() - timedelta(days=7)
    recent = perf.filter(timestamp__gte=week_ago).count()

    # Quiz results
    quiz_results = QuizResult.objects.filter(user=user).order_by('-taken_at')[:20]
    avg_quiz_score = QuizResult.objects.filter(user=user).aggregate(
        avg=Sum('score') / Count('id')
    )['avg'] or 0

    # Performance by category (if exercise has category)
    category_stats = {}
    for p in perf:
        cat = p.exercise.category or 'Sem categoria'
        if cat not in category_stats:
            category_stats[cat] = {'total': 0, 'correct': 0}
        category_stats[cat]['total'] += 1
        if p.correct:
            category_stats[cat]['correct'] += 1

    context = {
        'user': user,
        'total_attempts': total,
        'correct': correct,
        'accuracy': round(accuracy, 2),
        'recent_attempts': recent,
        'quiz_results': quiz_results,
        'avg_quiz_score': round(avg_quiz_score, 2),
        'category_stats': category_stats,
    }
    return render(request, 'panel/user_performance.html', context)


@staff_member_required
def performance_records(request):
    """List all performance records with filters."""
    records = PerformanceRecord.objects.select_related('user', 'exercise').order_by('-timestamp')

    user_filter = request.GET.get('user')
    correct_filter = request.GET.get('correct')

    if user_filter:
        records = records.filter(user__username__icontains=user_filter)
    if correct_filter == 'correct':
        records = records.filter(correct=True)
    elif correct_filter == 'incorrect':
        records = records.filter(correct=False)

    from django.core.paginator import Paginator
    paginator = Paginator(records, 50)
    page_num = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_num)
    except:
        page_obj = paginator.page(1)

    context = {
        'page_obj': page_obj,
        'user_filter': user_filter,
        'correct_filter': correct_filter,
    }
    return render(request, 'panel/performance_records.html', context)


@staff_member_required
def quiz_results_view(request):
    """List all quiz results with filters."""
    results = QuizResult.objects.select_related('user', 'quiz').order_by('-taken_at')

    user_filter = request.GET.get('user')
    quiz_filter = request.GET.get('quiz')

    if user_filter:
        results = results.filter(user__username__icontains=user_filter)
    if quiz_filter:
        results = results.filter(quiz__title__icontains=quiz_filter)

    from django.core.paginator import Paginator
    paginator = Paginator(results, 25)
    page_num = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_num)
    except:
        page_obj = paginator.page(1)

    context = {
        'page_obj': page_obj,
        'user_filter': user_filter,
        'quiz_filter': quiz_filter,
    }
    return render(request, 'panel/quiz_results.html', context)
