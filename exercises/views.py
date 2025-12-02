from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from .models import Exercise, PerformanceRecord
from .forms import ExerciseForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
try:
    from rapidfuzz import fuzz
except Exception:
    fuzz = None


def can_edit_exercise(user, exercise):
    """Check if user can edit an exercise.
    
    Rules:
    - Creator can always edit their own exercise
    - Staff can edit shared exercises
    - Regular users cannot edit shared exercises created by others
    """
    if not user.is_authenticated:
        return False
    if exercise.created_by == user:
        return True
    if user.is_staff and exercise.is_shared:
        return True
    return False


def can_delete_exercise(user, exercise):
    """Check if user can delete an exercise.
    
    Same rules as can_edit_exercise
    """
    return can_edit_exercise(user, exercise)


class ExerciseListView(ListView):
    model = Exercise
    template_name = 'exercises/list.html'
    paginate_by = 15

    def get_queryset(self):
        from django.db.models import Q
        # Show user's personal exercises + all shared exercises
        qs = Exercise.objects.filter(
            Q(created_by=self.request.user) | Q(is_shared=True)
        )
        q = self.request.GET.get('q')
        level = self.request.GET.get('level')
        category = self.request.GET.get('category')
        etype = self.request.GET.get('type')
        exercise_type = self.request.GET.get('exercise_type')
        done_filter = self.request.GET.get('done')
        
        if q:
            qs = qs.filter(question__icontains=q) | qs.filter(answer__icontains=q)
        if level:
            qs = qs.filter(level__icontains=level)
        if category:
            qs = qs.filter(category__icontains=category)
        if etype or exercise_type:
            filter_type = etype or exercise_type
            qs = qs.filter(exercise_type=filter_type)
        
        # Filter by completion status
        if done_filter == 'done':
            exercise_ids = PerformanceRecord.objects.filter(user=self.request.user).values_list('exercise_id', flat=True).distinct()
            qs = qs.filter(id__in=exercise_ids)
        elif done_filter == 'undone':
            exercise_ids = PerformanceRecord.objects.filter(user=self.request.user).values_list('exercise_id', flat=True).distinct()
            qs = qs.exclude(id__in=exercise_ids)
        
        return qs.order_by('id')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add completion status for each exercise on current page
        # Check if user has attempted this exercise (regardless of correct/incorrect)
        user_attempts = PerformanceRecord.objects.filter(
            user=self.request.user
        ).values_list('exercise_id', flat=True).distinct()
        
        # Mark exercises as done if they have any attempts
        for exercise in context.get('object_list', []):
            exercise.is_done = exercise.id in user_attempts
        
        # Also check page_obj for pagination scenarios
        if 'page_obj' in context:
            for exercise in context['page_obj']:
                exercise.is_done = exercise.id in user_attempts
        
        context['done_filter'] = self.request.GET.get('done', '')
        context['exercise_type'] = self.request.GET.get('exercise_type', '')
        return context


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


@login_required
def create_exercise(request):
    """Create a new exercise."""
    if request.method == 'POST':
        form = ExerciseForm(request.POST)
        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.created_by = request.user
            exercise.save()
            return redirect('exercises:detail', pk=exercise.pk)
    else:
        form = ExerciseForm()
    
    return render(request, 'exercises/form.html', {'form': form})


@login_required
def edit_exercise(request, pk):
    """Edit an existing exercise."""
    exercise = get_object_or_404(Exercise, pk=pk)
    
    if not can_edit_exercise(request.user, exercise):
        raise PermissionDenied(
            "Você não pode editar exercício compartilhado criado por outros usuários."
        )
    
    if request.method == 'POST':
        form = ExerciseForm(request.POST, instance=exercise)
        if form.is_valid():
            # Prevent regular users from marking shared exercises
            if not request.user.is_staff:
                if form.instance.is_shared and form.instance.created_by != request.user:
                    raise PermissionDenied(
                        "Apenas administradores podem compartilhar exercícios."
                    )
            form.save()
            return redirect('exercises:detail', pk=exercise.pk)
    else:
        form = ExerciseForm(instance=exercise)
    
    return render(request, 'exercises/form.html', {'form': form, 'exercise': exercise})


@login_required
def delete_exercise(request, pk):
    """Delete an exercise."""
    exercise = get_object_or_404(Exercise, pk=pk)
    
    if not can_delete_exercise(request.user, exercise):
        raise PermissionDenied(
            "Você não pode deletar exercício compartilhado criado por outros usuários."
        )
    
    if request.method == 'POST':
        exercise.delete()
        return redirect('exercises:list')
    
    return render(request, 'exercises/confirm_delete.html', {'exercise': exercise})
