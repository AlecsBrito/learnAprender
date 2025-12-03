from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Vocabulary
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .utils import generate_exercises_for_vocab
from exercises.models import Exercise
from exercises.utils import deduplicate_exercises  # Função de deduplicação
from django.db import transaction


def can_edit_vocab(user, vocab):
    """Check if user can edit a vocabulary item.
    
    Rules:
    - Creator can always edit their own vocab
    - Staff can edit shared vocab
    - Regular users cannot edit shared vocab created by others
    """
    if not user.is_authenticated:
        return False
    if vocab.created_by == user:
        return True
    if user.is_staff and vocab.is_shared:
        return True
    return False


def can_delete_vocab(user, vocab):
    """Check if user can delete a vocabulary item.
    
    Same rules as can_edit_vocab
    """
    return can_edit_vocab(user, vocab)


class VocabListView(ListView):
    model = Vocabulary
    template_name = 'vocab/list.html'
    paginate_by = 20

    def get_queryset(self):
        from django.db.models import Q
        # Show user's personal vocab + all shared vocab
        qs = Vocabulary.objects.filter(
            Q(created_by=self.request.user) | Q(is_shared=True)
        )
        
        # Filter by vocab type (shared/personal/all)
        vocab_type = self.request.GET.get('vocab_type')
        if vocab_type == 'shared':
            qs = qs.filter(is_shared=True)
        elif vocab_type == 'personal':
            qs = qs.filter(created_by=self.request.user, is_shared=False)
        
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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vocab_type'] = self.request.GET.get('vocab_type', 'all')
        return context


class VocabCreateView(LoginRequiredMixin, CreateView):
    model = Vocabulary
    fields = ['word', 'translation', 'example', 'category', 'level', 'tags', 'is_shared']
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
    fields = ['word', 'translation', 'example', 'category', 'level', 'tags', 'is_shared']
    template_name = 'vocab/form.html'
    success_url = reverse_lazy('vocab:list')
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not can_edit_vocab(self.request.user, obj):
            raise PermissionDenied(
                "Você não pode editar vocabulário compartilhado criado por outros usuários."
            )
        return obj
    
    def form_valid(self, form):
        # Prevent regular users from marking personal vocab as shared
        if not self.request.user.is_staff:
            if form.instance.is_shared and form.instance.created_by != self.request.user:
                raise PermissionDenied(
                    "Apenas administradores podem compartilhar vocabulário."
                )
        return super().form_valid(form)


class VocabDeleteView(LoginRequiredMixin, DeleteView):
    model = Vocabulary
    template_name = 'vocab/confirm_delete.html'
    success_url = reverse_lazy('vocab:list')
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not can_delete_vocab(self.request.user, obj):
            raise PermissionDenied(
                "Você não pode deletar vocabulário compartilhado criado por outros usuários."
            )
        return obj


@login_required
def generate_exercises_from_vocab(request, pk):
    vocab = get_object_or_404(Vocabulary, pk=pk)
    if request.method != 'POST':
        # If accessed by GET, show a simple confirmation page
        return render(request, 'vocab/confirm_generate.html', {'vocab': vocab})

    # prepare a distractor pool (other vocabulary entries)
    pool = list(Vocabulary.objects.exclude(pk=pk)[:50])
    generated = generate_exercises_for_vocab(vocab, distractor_pool=pool)

    # Remover duplicatas antes de salvar
    generated = deduplicate_exercises(generated, user=request.user)

    created = []
    with transaction.atomic():
        for ex in generated:
            ex.created_by = request.user
            ex.save()
            created.append(ex)

    if created:
        messages.success(request, f'Gerado {len(created)} exercício(s) a partir de "{vocab.word}".')
    else:
        messages.warning(request, f'Nenhum exercício novo foi criado (todos eram duplicatas).')
    return redirect('vocab:detail', pk=pk)


@login_required
def generate_exercises_from_all(request):
    if request.method != 'POST':
        return render(request, 'vocab/confirm_generate_all.html')

    qs = Vocabulary.objects.all()
    total = 0
    duplicates_skipped = 0
    with transaction.atomic():
        pool = list(qs)
        for v in qs:
            gen = generate_exercises_for_vocab(v, distractor_pool=pool)
            # Remover duplicatas
            gen = deduplicate_exercises(gen, user=request.user)
            for ex in gen:
                ex.created_by = request.user
                ex.save()
                total += 1
            duplicates_skipped += len(generate_exercises_for_vocab(v, distractor_pool=pool)) - len(gen)

    msg = f'Gerados {total} exercícios a partir do vocabulário.'
    if duplicates_skipped > 0:
        msg += f' ({duplicates_skipped} duplicatas foram ignoradas.)'
    messages.success(request, msg)
    return redirect('vocab:list')


@login_required
def generate_random_exercises(request):
    """Generate exercises with random vocabulary words from API sources."""
    import random
    from .utils import generate_exercises_from_random_words, get_random_words, fetch_word_definition_and_translation
    
    if request.method != 'POST':
        return render(request, 'vocab/confirm_generate_random.html', {'total_words': 'unlimited'})
    
    # Get count from POST (default 10, max 30)
    count = int(request.POST.get('count', 10))
    count = min(count, 30)  # Limit to 30 to avoid too many API calls
    
    try:
        # Get random words
        random_words = get_random_words(count)
        
        # First, add words to vocabulary
        vocab_created = []
        for word in random_words:
            try:
                definition, translation = fetch_word_definition_and_translation(word)
                if translation:
                    # Check if word already exists in user's vocabulary
                    existing = Vocabulary.objects.filter(
                        created_by=request.user,
                        word__iexact=word
                    ).first()
                    
                    if not existing:
                        vocab = Vocabulary.objects.create(
                            word=word,
                            translation=translation,
                            example=definition or '',
                            category='Random Words',
                            level='beginner',
                            created_by=request.user,
                            is_shared=False,
                        )
                        vocab_created.append(vocab)
            except Exception:
                pass
        
        # Then generate exercises from the created vocabularies
        exercises = generate_exercises_from_random_words(count=count, user_category='Random Words')
        
        # Remover duplicatas antes de salvar
        exercises = deduplicate_exercises(exercises, user=request.user)
        
        total = 0
        with transaction.atomic():
            for ex in exercises:
                ex.created_by = request.user
                ex.save()
                total += 1
        
        vocab_count = len(vocab_created)
        if total > 0:
            messages.success(
                request, 
                f'✨ Adicionadas {vocab_count} palavra(s) ao vocabulário e gerados {total} exercício(s)!'
            )
        else:
            messages.warning(request, 'Não foi possível gerar exercícios (todos eram duplicatas). Tente novamente.')
    except Exception as e:
        messages.error(request, f'Erro ao gerar exercícios: {str(e)}')
        return redirect('vocab:list')
    
    return redirect('exercises:list')
