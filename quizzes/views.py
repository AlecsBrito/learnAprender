from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from exercises.models import Exercise
from .models import Quiz, QuizResult
from django.contrib.auth.models import User
import random
try:
    from rapidfuzz import fuzz
except Exception:
    fuzz = None


def index(request):
    quizzes = Quiz.objects.all().order_by('-created_at')[:20]
    return render(request, 'quizzes/index.html', {'quizzes': quizzes})


@login_required
def generate_quiz(request):
    if request.method == 'POST':
        level = request.POST.get('level')
        theme = request.POST.get('theme')
        count = int(request.POST.get('count') or 10)
        qs = Exercise.objects.all()
        if level:
            qs = qs.filter(level__icontains=level)
        if theme:
            qs = qs.filter(category__icontains=theme)
        pool = list(qs)
        selected = random.sample(pool, min(len(pool), count))
        quiz = Quiz.objects.create(title=f"Quiz {theme or 'General'} - {level or 'All'}", level=level or '', theme=theme or '', created_by=request.user)
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
