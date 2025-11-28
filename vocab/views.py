from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Vocabulary
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from .utils import generate_exercises_for_vocab
from exercises.models import Exercise
from django.db import transaction


class VocabListView(ListView):
    model = Vocabulary
    template_name = 'vocab/list.html'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q')
        level = self.request.GET.get('level')
        category = self.request.GET.get('category')
        if q:
            qs = qs.filter(word__icontains=q) | qs.filter(translation__icontains=q)
        if level:
            qs = qs.filter(level=level)
        if category:
            qs = qs.filter(category__icontains=category)
        return qs.order_by('word')


class VocabCreateView(LoginRequiredMixin, CreateView):
    model = Vocabulary
    fields = ['word', 'translation', 'example', 'category', 'level', 'tags']
    template_name = 'vocab/form.html'
    success_url = reverse_lazy('vocab:list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class VocabDetailView(DetailView):
    model = Vocabulary
    template_name = 'vocab/detail.html'


class VocabUpdateView(LoginRequiredMixin, UpdateView):
    model = Vocabulary
    fields = ['word', 'translation', 'example', 'category', 'level', 'tags']
    template_name = 'vocab/form.html'
    success_url = reverse_lazy('vocab:list')


class VocabDeleteView(LoginRequiredMixin, DeleteView):
    model = Vocabulary
    template_name = 'vocab/confirm_delete.html'
    success_url = reverse_lazy('vocab:list')


@login_required
def generate_exercises_from_vocab(request, pk):
    vocab = get_object_or_404(Vocabulary, pk=pk)
    if request.method != 'POST':
        # If accessed by GET, show a simple confirmation page
        return render(request, 'vocab/confirm_generate.html', {'vocab': vocab})

    # prepare a distractor pool (other vocabulary entries)
    pool = list(Vocabulary.objects.exclude(pk=pk)[:50])
    generated = generate_exercises_for_vocab(vocab, distractor_pool=pool)

    created = []
    with transaction.atomic():
        for ex in generated:
            ex.created_by = request.user
            ex.save()
            created.append(ex)

    messages.success(request, f'Gerado {len(created)} exercício(s) a partir de "{vocab.word}".')
    return redirect('vocab:detail', pk=pk)


@login_required
def generate_exercises_from_all(request):
    if request.method != 'POST':
        return render(request, 'vocab/confirm_generate_all.html')

    qs = Vocabulary.objects.all()
    total = 0
    with transaction.atomic():
        pool = list(qs)
        for v in qs:
            gen = generate_exercises_for_vocab(v, distractor_pool=pool)
            for ex in gen:
                ex.created_by = request.user
                ex.save()
                total += 1

    messages.success(request, f'Gerados {total} exercícios a partir do vocabulário.')
    return redirect('vocab:list')
