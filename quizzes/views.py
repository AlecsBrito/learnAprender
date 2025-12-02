from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
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
    # Show user's personal quizzes + all shared quizzes
    if request.user.is_authenticated:
        quizzes = Quiz.objects.filter(
            Q(created_by=request.user) | Q(is_shared=True)
        ).order_by('-created_at')[:20]
    else:
        # Non-authenticated users see only shared quizzes
        quizzes = Quiz.objects.filter(is_shared=True).order_by('-created_at')[:20]
    return render(request, 'quizzes/index.html', {'quizzes': quizzes})


@login_required
def generate_quiz(request):
    if request.method == 'POST':
        level = request.POST.get('level')
        theme = request.POST.get('theme')
        count = int(request.POST.get('count') or 10)
        is_shared = request.POST.get('is_shared') == 'on'
        qs = Exercise.objects.all()
        if level:
            qs = qs.filter(level__icontains=level)
        if theme:
            qs = qs.filter(category__icontains=theme)
        pool = list(qs)
        selected = random.sample(pool, min(len(pool), count))
        quiz = Quiz.objects.create(
            title=f"Quiz {theme or 'General'} - {level or 'All'}", 
            level=level or '', 
            theme=theme or '', 
            created_by=request.user,
            is_shared=is_shared
        )
        quiz.questions.set(selected)
        quiz.save()
        return redirect('quizzes:take', quiz_id=quiz.id)

    return render(request, 'quizzes/generate.html')


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
    """View quiz details."""
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    can_edit = can_edit_quiz(request.user, quiz)
    questions = quiz.questions.all()
    return render(request, 'quizzes/detail.html', {
        'quiz': quiz,
        'questions': questions,
        'can_edit': can_edit
    })

