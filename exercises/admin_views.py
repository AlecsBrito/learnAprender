from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from .models import Exercise
from .forms import ExerciseForm


@staff_member_required
def exercise_list_admin(request):
    qs = Exercise.objects.all().order_by('-created_at')
    q = request.GET.get('q')
    etype = request.GET.get('type')
    level = request.GET.get('level')
    category = request.GET.get('category')
    if q:
        qs = qs.filter(question__icontains=q) | qs.filter(answer__icontains=q)
    if etype:
        qs = qs.filter(exercise_type=etype)
    if level:
        qs = qs.filter(level__icontains=level)
    if category:
        qs = qs.filter(category__icontains=category)

    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(qs, 25)
    page_num = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_num)
    except:
        page_obj = paginator.page(1)

    # Bulk delete
    action = request.POST.get('action')
    selected = request.POST.getlist('selected')
    if action and selected:
        ids = [int(x) for x in selected if x.isdigit()]
        if action == 'delete':
            Exercise.objects.filter(pk__in=ids).delete()
            messages.success(request, f'Removidos {len(ids)} exercícios.')
            return redirect('panel_exercises:exercise_list')

    return render(request, 'panel/exercise_list.html', {'page_obj': page_obj, 'q': q, 'etype': etype, 'level': level, 'category': category})


@staff_member_required
def exercise_create_admin(request):
    if request.method == 'POST':
        form = ExerciseForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_by = request.user
            obj.save()
            messages.success(request, 'Exercício criado.')
            return redirect('panel_exercises:exercise_list')
    else:
        form = ExerciseForm()
    return render(request, 'panel/exercise_form.html', {'form': form})


@staff_member_required
def exercise_edit_admin(request, pk):
    obj = get_object_or_404(Exercise, pk=pk)
    if request.method == 'POST':
        form = ExerciseForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exercício atualizado.')
            return redirect('panel_exercises:exercise_list')
    else:
        form = ExerciseForm(instance=obj)
    return render(request, 'panel/exercise_form.html', {'form': form, 'object': obj})


@staff_member_required
def exercise_delete_admin(request, pk):
    obj = get_object_or_404(Exercise, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Exercício removido.')
        return redirect('panel_exercises:exercise_list')
    return render(request, 'panel/exercise_confirm_delete.html', {'object': obj})
