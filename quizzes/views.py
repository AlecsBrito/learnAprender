from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from datetime import timedelta
from exercises.models import Exercise
from .models import Quiz, QuizResult
from .forms import QuizForm
from django.contrib.auth.models import User
import random
try:
    from rapidfuzz import fuzz
except Exception:
    fuzz = None


def can_edit_quiz(user, quiz):
    """Check if user can edit a quiz.
    
    Rules:
    - Creator can always edit their own quiz
    - Staff can edit shared quizzes
    - Regular users cannot edit shared quizzes created by others
    """
    if not user.is_authenticated:
        return False
    if quiz.created_by == user:
        return True
    if user.is_staff and quiz.is_shared:
        return True
    return False


def can_delete_quiz(user, quiz):
    """Check if user can delete a quiz.
    
    Same rules as can_edit_quiz
    """
    return can_edit_quiz(user, quiz)


def index(request):
    from django.db.models import Q
    # Fetch base queryset (user's + shared)
    if request.user.is_authenticated:
        qs = Quiz.objects.filter(Q(created_by=request.user) | Q(is_shared=True))
    else:
        qs = Quiz.objects.filter(is_shared=True)

    # Filtering from query params
    theme = request.GET.get('theme', '').strip()
    level = request.GET.get('level', '').strip()
    if theme:
        qs = qs.filter(Q(theme__iexact=theme) | Q(theme__icontains=theme))
    if level:
        qs = qs.filter(level__icontains=level)

    quizzes = qs.order_by('-created_at')[:50]

    # Provide available categories (themes) for filters based on exercises visible to user
    if request.user.is_authenticated:
        exercise_qs = Exercise.objects.filter(Q(created_by=request.user) | Q(is_shared=True))
    else:
        exercise_qs = Exercise.objects.filter(is_shared=True)
    categories = exercise_qs.values_list('category', flat=True).distinct()
    categories = [c for c in categories if c]

    return render(request, 'quizzes/index.html', {'quizzes': quizzes, 'categories': categories})


@login_required
def preview_quiz_count(request):
    """Return JSON with counts of available exercises for given filters."""
    from django.http import JsonResponse
    level = request.GET.get('level')
    themes = request.GET.getlist('themes') or request.GET.getlist('theme') or []

    # Only include procedural exercises (gap-fill and translation, exclude MCQ)
    qs = Exercise.objects.filter(
        Q(created_by=request.user) | Q(is_shared=True) | Q(created_by__isnull=True),
        exercise_type__in=['gap', 'translate']
    )
    if level:
        qs = qs.filter(level__icontains=level)
    if themes:
        themes_clean = [t.strip() for t in themes if t and t.strip()]
        if themes_clean:
            q_theme = Q()
            for t in themes_clean:
                q_theme |= Q(category__iexact=t) | Q(category__icontains=t)
            qs = qs.filter(q_theme)

    total = qs.count()
    shared = qs.filter(is_shared=True).count()
    personal = qs.exclude(is_shared=True).filter(created_by=request.user).count()

    return JsonResponse({'total': total, 'shared': shared, 'personal': personal})


@login_required
def generate_quiz(request):
    # Local import to avoid circular import issues
    from exercises.models import PerformanceRecord

    if request.method == 'POST':
        level = request.POST.get('level')
        themes = request.POST.getlist('themes') or request.POST.getlist('theme') or []
        count = int(request.POST.get('count') or 10)
        is_shared = request.POST.get('is_shared') == 'on'

        # Filter exercises visible to this user (include global exercises with no creator)
        # Only include procedural exercises (gap-fill and translation, exclude MCQ)
        qs = Exercise.objects.filter(
            Q(created_by=request.user) | Q(is_shared=True) | Q(created_by__isnull=True),
            exercise_type__in=['gap', 'translate']
        )
        if level:
            qs = qs.filter(level__icontains=level)
        if themes:
            themes_clean = [t.strip() for t in themes if t and t.strip()]
            if themes_clean:
                q_theme = Q()
                for t in themes_clean:
                    q_theme |= Q(category__iexact=t) | Q(category__icontains=t)
                qs = qs.filter(q_theme)

        pool = list(qs)
        if not pool:
            messages.warning(request, 'Nenhum exercício disponível para os filtros selecionados.')
            return redirect('quizzes:generate')

        # Selection heuristics:
        # 1) Avoid exercises recently used in quizzes (within last 30 days)
        # 2) Prefer exercises the user has NOT attempted recently (or never attempted)
        # 3) Aim to balance exercise types (mcq/gap/translate)
        
        # Build map of exercises used in recent quizzes
        recent_cutoff = timezone.now() - timedelta(days=30)
        recent_quiz_ids = Quiz.objects.filter(created_by=request.user, created_at__gte=recent_cutoff).values_list('id', flat=True)
        recently_used_ids = set(Quiz.objects.filter(id__in=recent_quiz_ids).values_list('questions__id', flat=True))
        
        last_attempt_map = {}
        for ex in pool:
            la = PerformanceRecord.objects.filter(user=request.user, exercise=ex).order_by('-timestamp').first()
            last_attempt_map[ex.id] = (la.timestamp if la else None, ex.id in recently_used_ids)

        # Group exercises by type
        by_type = {}
        for ex in pool:
            by_type.setdefault(ex.exercise_type, []).append(ex)

        types = list(by_type.keys())
        if not types:
            selected = random.sample(pool, min(len(pool), count))
        else:
            # target quota per type (try to distribute evenly)
            quotas = {}
            base = count // len(types)
            rem = count % len(types)
            for i, t in enumerate(types):
                quotas[t] = base + (1 if i < rem else 0)

            selected = []
            # For each type, sort by: not recently-used, then unseen, then oldest attempt
            for t in types:
                items = by_type.get(t, [])
                def sort_key(e):
                    ts, is_recent = last_attempt_map.get(e.id, (None, False))
                    return (is_recent, ts is not None, ts or 0)  # Prioritize: not recent, not attempted, oldest attempt
                items_sorted = sorted(items, key=sort_key)
                take = min(len(items_sorted), quotas.get(t, 0))
                selected.extend(items_sorted[:take])

            # If we still need more (not enough across types), fill from remaining pool sorted by recency
            if len(selected) < count:
                remaining = [e for e in pool if e not in selected]
                def sort_key_remaining(e):
                    ts, is_recent = last_attempt_map.get(e.id, (None, False))
                    return (is_recent, ts is not None, ts or 0)
                remaining_sorted = sorted(remaining, key=sort_key_remaining)
                need = count - len(selected)
                selected.extend(remaining_sorted[:need])

            # Ensure not selecting more than available
            selected = selected[:min(len(pool), count)]

        # Create quiz with auto-selected questions
        title_theme = ','.join(themes_clean) if themes else ''
        quiz = Quiz.objects.create(
            title=f"Quiz {title_theme or 'General'} - {level or 'All'}",
            level=level or '',
            theme=title_theme or '',
            created_by=request.user,
            is_shared=is_shared,
        )
        if selected:
            quiz.questions.set(selected)
            quiz.save()

        messages.success(request, f'Quiz criado com {len(selected)} pergunta(s).')
        return redirect('quizzes:detail', quiz_id=quiz.id)

    # GET - provide categories for the form (only from procedural exercises)
    if request.user.is_authenticated:
        exercise_qs = Exercise.objects.filter(
            Q(created_by=request.user) | Q(is_shared=True) | Q(created_by__isnull=True),
            exercise_type__in=['gap', 'translate']
        )
    else:
        exercise_qs = Exercise.objects.filter(is_shared=True, exercise_type__in=['gap', 'translate'])
    categories = exercise_qs.values_list('category', flat=True).distinct()
    categories = [c for c in categories if c]
    return render(request, 'quizzes/generate.html', {'categories': categories})


@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    questions = list(quiz.questions.all())
    if request.method == 'POST':
        results = {}
        correct_count = 0
        for q in questions:
            field = f'q_{q.id}'
            ans = request.POST.get(field, '').strip()
            is_correct = False
            if q.exercise_type == 'mcq':
                is_correct = ans and ans.strip().lower() == q.answer.strip().lower()
            else:
                given = ans.strip()
                expected = q.answer.strip()
                if fuzz:
                    score = fuzz.token_sort_ratio(given, expected)
                    is_correct = score >= 80
                else:
                    is_correct = expected.lower() in given.lower() or given.lower() in expected.lower()
            results[str(q.id)] = {'given': ans, 'correct': is_correct, 'expected': q.answer}
            if is_correct:
                correct_count += 1
            # record performance per question
            from exercises.models import PerformanceRecord
            PerformanceRecord.objects.create(user=request.user, exercise=q, correct=is_correct)

        score = (correct_count / max(1, len(questions))) * 100.0
        qr = QuizResult.objects.create(user=request.user, quiz=quiz, score=score, details=results)
        return redirect('quizzes:result', result_id=qr.id)

    return render(request, 'quizzes/take.html', {'quiz': quiz, 'questions': questions})


@login_required
def quiz_result(request, result_id):
    res = get_object_or_404(QuizResult, pk=result_id)
    return render(request, 'quizzes/result.html', {'result': res})


@login_required
def edit_quiz(request, quiz_id):
    """Edit quiz details."""
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    
    if not can_edit_quiz(request.user, quiz):
        raise PermissionDenied(
            "Você não pode editar quiz compartilhado criado por outros usuários."
        )
    
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            # Prevent regular users from marking shared quizzes
            if not request.user.is_staff:
                if form.instance.is_shared and form.instance.created_by != request.user:
                    raise PermissionDenied(
                        "Apenas administradores podem compartilhar quizzes."
                    )
            form.save()
            return redirect('quizzes:detail', quiz_id=quiz.id)
    else:
        form = QuizForm(instance=quiz)
    
    return render(request, 'quizzes/form.html', {'form': form, 'quiz': quiz})


@login_required
def delete_quiz(request, quiz_id):
    """Delete quiz."""
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    
    if not can_delete_quiz(request.user, quiz):
        raise PermissionDenied(
            "Você não pode deletar quiz compartilhado criado por outros usuários."
        )
    
    if request.method == 'POST':
        quiz.delete()
        return redirect('quizzes:index')
    
    return render(request, 'quizzes/confirm_delete.html', {'quiz': quiz})


@login_required
def detail_quiz(request, quiz_id):
    """View quiz details and add/remove questions."""
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    can_edit = can_edit_quiz(request.user, quiz)
    questions = quiz.questions.all()
    
    # Handle adding questions to quiz
    if request.method == 'POST' and can_edit:
        action = request.POST.get('action')
        
        if action == 'add_questions':
            selected_ids = request.POST.getlist('question_ids')
            if selected_ids:
                exercises = Exercise.objects.filter(id__in=selected_ids)
                quiz.questions.add(*exercises)
                quiz.save()
        
        elif action == 'remove_question':
            question_id = request.POST.get('question_id')
            if question_id:
                quiz.questions.remove(question_id)
                quiz.save()
        
        return redirect('quizzes:detail', quiz_id=quiz.id)
    
    # Get available exercises to add (not already in quiz)
    available_exercises = Exercise.objects.exclude(quiz__id=quiz.id) if can_edit else None
    
    return render(request, 'quizzes/detail.html', {
        'quiz': quiz,
        'questions': questions,
        'can_edit': can_edit,
        'available_exercises': available_exercises
    })

