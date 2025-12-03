from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from .models import Vocabulary
from .forms import VocabularyForm
from .utils import generate_exercises_for_vocab
from .admin_utils import get_paginated_queryset, filter_by_search_and_level, filter_by_category, filter_by_sharing  # Funções compartilhadas
from exercises.models import Exercise
from django.db import transaction


@staff_member_required
def vocab_list_admin(request):
    qs = Vocabulary.objects.all().order_by('word')
    q = request.GET.get('q')
    level = request.GET.get('level')
    category = request.GET.get('category')
    shared_filter = request.GET.get('shared')  # 'shared', 'personal', or None for all
    
    # Usar funções compartilhadas para filtros
    qs = filter_by_search_and_level(qs, q, level, ['word', 'translation'])
    qs = filter_by_category(qs, category)
    qs = filter_by_sharing(qs, shared_filter)

    # Pagination usando função compartilhada
    page_obj = get_paginated_queryset(qs, request.GET.get('page', 1), per_page=25)

    # Bulk actions
    action = request.POST.get('action')
    selected = request.POST.getlist('selected')
    if action and selected:
        ids = [int(x) for x in selected if x.isdigit()]
        if action == 'delete':
            Vocabulary.objects.filter(pk__in=ids).delete()
            messages.success(request, f'Removidos {len(ids)} itens.')
            return redirect('panel:vocab_list')
        elif action == 'generate':
            total = 0
            with transaction.atomic():
                pool = list(Vocabulary.objects.all()[:100])
                for v in Vocabulary.objects.filter(pk__in=ids):
                    gen = generate_exercises_for_vocab(v, distractor_pool=pool)
                    for ex in gen:
                        ex.created_by = request.user
                        ex.save()
                        total += 1
            messages.success(request, f'Gerados {total} exercícios.')
            return redirect('panel:vocab_list')

    return render(request, 'panel/vocab_list.html', {
        'page_obj': page_obj, 'q': q, 'level': level, 'category': category,
        'shared_filter': shared_filter
    })


@staff_member_required
def vocab_create_admin(request):
    if request.method == 'POST':
        form = VocabularyForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_by = request.user
            obj.save()
            messages.success(request, 'Vocabulary criado.')
            return redirect('panel:vocab_list')
    else:
        form = VocabularyForm()
    return render(request, 'panel/vocab_form.html', {'form': form})


@staff_member_required
def vocab_edit_admin(request, pk):
    obj = get_object_or_404(Vocabulary, pk=pk)
    if request.method == 'POST':
        form = VocabularyForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vocabulary atualizado.')
            return redirect('panel:vocab_list')
    else:
        form = VocabularyForm(instance=obj)
    return render(request, 'panel/vocab_form.html', {'form': form, 'object': obj})


@staff_member_required
def vocab_delete_admin(request, pk):
    obj = get_object_or_404(Vocabulary, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Vocabulary removido.')
        return redirect('panel:vocab_list')
    return render(request, 'panel/vocab_confirm_delete.html', {'object': obj})


@staff_member_required
def vocab_generate_exercises_admin(request, pk):
    obj = get_object_or_404(Vocabulary, pk=pk)
    if request.method != 'POST':
        return render(request, 'panel/vocab_confirm_generate.html', {'object': obj})

    pool = list(Vocabulary.objects.exclude(pk=pk)[:50])
    generated = generate_exercises_for_vocab(obj, distractor_pool=pool)
    created = 0
    with transaction.atomic():
        for ex in generated:
            ex.created_by = request.user
            ex.save()
            created += 1
    messages.success(request, f'Gerados {created} exercícios a partir de "{obj.word}"')
    return redirect('panel:vocab_list')
