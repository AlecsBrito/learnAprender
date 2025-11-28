from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from .models import Exercise, PerformanceRecord
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
try:
    from rapidfuzz import fuzz
except Exception:
    fuzz = None


class ExerciseListView(ListView):
    model = Exercise
    template_name = 'exercises/list.html'
    paginate_by = 15

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q')
        level = self.request.GET.get('level')
        category = self.request.GET.get('category')
        etype = self.request.GET.get('type')
        if q:
            qs = qs.filter(question__icontains=q) | qs.filter(answer__icontains=q)
        if level:
            qs = qs.filter(level__icontains=level)
        if category:
            qs = qs.filter(category__icontains=category)
        if etype:
            qs = qs.filter(exercise_type=etype)
        return qs.order_by('id')


class ExerciseDetailView(DetailView):
    model = Exercise
    template_name = 'exercises/detail.html'


@login_required
def take_exercise(request, pk):
    ex = get_object_or_404(Exercise, pk=pk)
    context = {'exercise': ex}
    if request.method == 'POST':
        user_answer = request.POST.get('answer', '').strip()
        correct = False
        # normalize comparisons
        def norm(s):
            return (s or '').strip()

        if ex.exercise_type == 'mcq':
            selected = request.POST.get('choice')
            correct = (selected is not None and norm(selected).lower() == norm(ex.answer).lower())
        else:
            # For gap and translate, use fuzzy matching if available
            given = norm(user_answer)
            expected = norm(ex.answer)
            if fuzz:
                score = fuzz.token_sort_ratio(given, expected)
                correct = score >= 80
            else:
                # fallback to simple substring or exact match
                correct = given.lower() == expected.lower() or expected.lower() in given.lower()

        PerformanceRecord.objects.create(user=request.user, exercise=ex, correct=correct)

        context.update({'submitted': True, 'correct': correct, 'user_answer': user_answer})
        return render(request, 'exercises/result.html', context)

    return render(request, 'exercises/take.html', context)
