from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from exercises.models import PerformanceRecord
from quizzes.models import QuizResult
from django.db.models import Count, Sum, Q, Avg
from .models import ReviewSchedule
from vocab.models import Vocabulary
from django.utils import timezone
from datetime import timedelta


def index(request):
    return render(request, 'reviews/index.html')


@login_required
def progress(request):
    """Show user's learning progress and accuracy."""
    user = request.user
    
    # Performance Records (Exercise attempts)
    all_attempts = PerformanceRecord.objects.filter(user=user)
    total_attempts = all_attempts.count()
    correct_attempts = all_attempts.filter(correct=True).count()
    accuracy = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
    
    # Quiz Results
    quiz_results = QuizResult.objects.filter(user=user)
    total_quizzes = quiz_results.count()
    avg_quiz_score = quiz_results.aggregate(avg_score=Avg('score'))['avg_score'] or 0
    
    # Performance by category
    category_stats = []
    categories = all_attempts.values_list('exercise__category', flat=True).distinct()
    for category in categories:
        cat_attempts = all_attempts.filter(exercise__category=category)
        cat_correct = cat_attempts.filter(correct=True).count()
        cat_total = cat_attempts.count()
        cat_accuracy = (cat_correct / cat_total * 100) if cat_total > 0 else 0
        category_stats.append({
            'category': category or 'Sin categoría',
            'attempts': cat_total,
            'correct': cat_correct,
            'accuracy': cat_accuracy
        })
    
    # Performance by exercise type
    type_stats = []
    types = all_attempts.values_list('exercise__exercise_type', flat=True).distinct()
    for ex_type in types:
        type_attempts = all_attempts.filter(exercise__exercise_type=ex_type)
        type_correct = type_attempts.filter(correct=True).count()
        type_total = type_attempts.count()
        type_accuracy = (type_correct / type_total * 100) if type_total > 0 else 0
        type_label = dict([
            ('mcq', 'Múltipla Escolha'),
            ('gap', 'Preencher Lacuna'),
            ('translate', 'Tradução')
        ]).get(ex_type, ex_type)
        type_stats.append({
            'type': type_label,
            'attempts': type_total,
            'correct': type_correct,
            'accuracy': type_accuracy
        })
    
    # Recent activity
    recent_attempts = all_attempts.select_related('exercise').order_by('-timestamp')[:10]
    recent_quizzes = quiz_results.select_related('quiz').order_by('-taken_at')[:10]
    
    context = {
        'total_attempts': total_attempts,
        'correct_attempts': correct_attempts,
        'incorrect_attempts': total_attempts - correct_attempts,
        'accuracy': accuracy,
        'total_quizzes': total_quizzes,
        'avg_quiz_score': avg_quiz_score,
        'category_stats': category_stats,
        'type_stats': type_stats,
        'recent_attempts': recent_attempts,
        'recent_quizzes': recent_quizzes,

    }
    @login_required
    def high_error_words(request):
        """Show vocabulary with highest error rates for the user."""
        user = request.user
    
        # Get all vocabularies the user has seen (via exercises)
        # Calculate error rate for each
        from django.db.models import F, Case, When, FloatField, Count as DbCount
    
        all_vocabs = Vocabulary.objects.filter(
            Q(created_by=user) | Q(is_shared=True)
        ).annotate(
            attempt_count=DbCount('performancerecord', filter=Q(performancerecord__user=user))
        ).filter(attempt_count__gt=0)
    
        high_error_words_list = []
        for vocab in all_vocabs:
            attempts = PerformanceRecord.objects.filter(user=user, exercise__question__icontains=vocab.word)
            if attempts.count() >= 2:  # Only show if attempted at least twice
                correct = attempts.filter(correct=True).count()
                total = attempts.count()
                error_rate = ((total - correct) / total * 100) if total > 0 else 0
                if error_rate >= 30:  # Show words with 30%+ error rate
                    high_error_words_list.append({
                        'vocab': vocab,
                        'attempts': total,
                        'errors': total - correct,
                        'error_rate': error_rate
                    })
    
        # Sort by error rate descending
        high_error_words_list.sort(key=lambda x: x['error_rate'], reverse=True)
    
        context = {
            'high_error_words': high_error_words_list[:20]  # Top 20 problematic words
        }
        return render(request, 'reviews/high_error_words.html', context)

    
    @login_required
    def schedule_review(request, vocab_id):
        """Schedule a vocabulary review for later."""
        vocab = Vocabulary.objects.get(pk=vocab_id)
        user = request.user
    
        if request.method == 'POST':
            days_offset = int(request.POST.get('days_offset', 1))
            scheduled_time = timezone.now() + timedelta(days=days_offset)
        
            # Create or update review schedule
            schedule, created = ReviewSchedule.objects.get_or_create(
                user=user,
                vocabulary=vocab,
                defaults={'scheduled_at': scheduled_time}
            )
            if not created:
                schedule.scheduled_at = scheduled_time
                schedule.save()
        
            return render(request, 'reviews/schedule_success.html', {
                'vocab': vocab,
                'scheduled_at': scheduled_time
            })
    
        return render(request, 'reviews/schedule_review.html', {'vocab': vocab})

    return render(request, 'reviews/progress.html', context)
    @login_required
    def scheduled_reviews(request):
        """Show user's scheduled reviews."""
        user = request.user
        today = timezone.now()
    
        # Get upcoming and overdue reviews
        all_scheduled = ReviewSchedule.objects.filter(user=user).select_related('vocabulary')
    
        overdue = all_scheduled.filter(scheduled_at__lt=today).order_by('scheduled_at')
        upcoming_today = all_scheduled.filter(
            scheduled_at__gte=today,
            scheduled_at__lt=today + timedelta(days=1)
        ).order_by('scheduled_at')
        upcoming_week = all_scheduled.filter(
            scheduled_at__gte=today + timedelta(days=1),
            scheduled_at__lt=today + timedelta(days=7)
        ).order_by('scheduled_at')
        upcoming_later = all_scheduled.filter(
            scheduled_at__gte=today + timedelta(days=7)
        ).order_by('scheduled_at')
    
        context = {
            'overdue': overdue,
            'upcoming_today': upcoming_today,
            'upcoming_week': upcoming_week,
            'upcoming_later': upcoming_later,
            'total_scheduled': all_scheduled.count()
        }
        return render(request, 'reviews/scheduled_reviews.html', context)
