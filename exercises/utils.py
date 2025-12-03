"""Utilities for generating gap-fill exercises from vocabulary."""

from vocab.models import Vocabulary
from .models import Exercise
from django.contrib.auth.models import User
import random


def generate_gap_fill_exercise(vocab: Vocabulary, user: User = None, is_shared: bool = False) -> Exercise:
    """Generate a gap-fill exercise from a vocabulary item.
    
    Creates an exercise where the user must fill in a blank word in a sentence.
    The sentence is built from the vocabulary example or a generic template.
    
    Args:
        vocab: Vocabulary item to create exercise from
        user: User creating the exercise (optional, for shared vocab)
        is_shared: Whether to mark as shared (default False)
        
    Returns:
        Exercise instance (not saved to DB)
    """
    word = vocab.word.strip()
    
    # Build the question with a gap (underscore)
    if vocab.example:
        # Use existing example, replace word with blank
        question = vocab.example.replace(word, "________")
    else:
        # Generate a generic sentence with gap
        question = f"Preencha a lacuna: ________ ({vocab.translation})"
    
    exercise = Exercise(
        question=question,
        exercise_type='gap',
        answer=word,
        level=vocab.level,
        category=vocab.category or 'Vocabulário',
        created_by=user or vocab.created_by,
        is_shared=is_shared,
    )
    
    return exercise


def create_gap_fill_exercises_batch(vocab_items: list, user: User = None, is_shared: bool = False, save: bool = False) -> list:
    """Create multiple gap-fill exercises from vocabulary items.
    
    Args:
        vocab_items: List of Vocabulary objects
        user: User creating the exercises
        is_shared: Whether to mark as shared
        save: Whether to save to database immediately
        
    Returns:
        List of Exercise instances (saved if save=True)
    """
    exercises = []
    
    for vocab in vocab_items:
        try:
            ex = generate_gap_fill_exercise(vocab, user, is_shared)
            if save:
                ex.save()
            exercises.append(ex)
        except Exception as e:
            print(f"Error creating gap-fill for {vocab.word}: {e}")
            continue
    
    return exercises


def get_suggestions_for_gap_fill(vocab: Vocabulary, num_suggestions: int = 4) -> dict:
    """Get suggestions for completing a gap-fill exercise.
    
    Returns the correct answer plus other distractors from similar vocabulary.
    
    Args:
        vocab: The vocabulary item being used
        num_suggestions: Total number of suggestions to return
        
    Returns:
        Dict with 'correct' (the word) and 'options' (list of suggestions including correct)
    """
    correct_word = vocab.word.strip()
    
    # Get similar vocabulary items (same category or level)
    similar_vocab = Vocabulary.objects.filter(
        level=vocab.level,
        is_shared=vocab.is_shared
    ).exclude(id=vocab.id)[:num_suggestions * 2]
    
    # Get random distractors
    distractors = [v.word for v in similar_vocab]
    random.shuffle(distractors)
    
    # Ensure we have enough distractors
    while len(distractors) < (num_suggestions - 1):
        # If not enough similar vocab, add any random vocabulary
        random_vocab = Vocabulary.objects.filter(
            is_shared=vocab.is_shared
        ).exclude(id=vocab.id).order_by('?')[:1]
        if random_vocab:
            distractors.append(random_vocab[0].word)
        else:
            break
    
    # Create options list with correct answer
    options = [correct_word] + distractors[:num_suggestions - 1]
    random.shuffle(options)
    
    return {
        'correct': correct_word,
        'options': options,
    }


# ============================================================================
# AVALIAÇÃO COMPARTILHADA - Funções reutilizáveis entre views
# ============================================================================

try:
    from rapidfuzz import fuzz
except Exception:
    fuzz = None


def normalize_answer(text):
    """Normaliza texto para comparação de respostas.
    
    Args:
        text (str): Texto a normalizar
    
    Returns:
        str: Texto normalizado (lowercase, sem espaços extras)
    """
    return text.strip().lower()


def check_answer_correctness(user_answer, expected_answer, exercise_type, choice=None):
    """
    Verifica se a resposta do usuário está correta.
    
    Esta função é compartilhada entre take_exercise e take_quiz para
    garantir consistência na avaliação.
    
    Args:
        user_answer (str): Resposta fornecida pelo usuário
        expected_answer (str): Resposta esperada
        exercise_type (str): Tipo de exercício ('mcq', 'gap', 'translate')
        choice (str): Opção selecionada para MCQ (opcional)
    
    Returns:
        bool: True se correto, False caso contrário
    """
    if exercise_type == 'mcq':
        return choice is not None and normalize_answer(choice) == normalize_answer(expected_answer)
    
    # Para gap e translate: fuzzy matching com 80% threshold
    given = normalize_answer(user_answer)
    expected = normalize_answer(expected_answer)
    
    if fuzz:
        score = fuzz.token_sort_ratio(given, expected)
        return score >= 80
    else:
        # Fallback: substring match se rapidfuzz não disponível
        return given == expected or expected in given


def get_procedural_exercises_queryset(base_qs):
    """
    Filtra queryset para apenas exercícios procedurais.
    
    Exercícios procedurais (gap-fill e translation) têm maior valor de
    aprendizado comparado a MCQ. Esta função é compartilhada entre
    multiple choice generation para garantir consistência.
    
    Args:
        base_qs (QuerySet): QuerySet base de exercícios
    
    Returns:
        QuerySet: QuerySet filtrado com apenas gap-fill e translation
    """
    return base_qs.filter(exercise_type__in=['gap', 'translate'])


def exercise_already_exists(question, exercise_type, user=None):
    """
    Verifica se um exercício com essa pergunta já existe.
    
    Usa normalização para detectar duplicatas mesmo com pequenas
    diferenças de espaçamento ou case.
    
    Args:
        question (str): Pergunta/texto do exercício
        exercise_type (str): Tipo de exercício (mcq/gap/translate)
        user (User): Usuário proprietário (opcional - se None, busca globalmente)
    
    Returns:
        bool: True se exercício duplicado já existe
    """
    from .models import Exercise
    from django.db.models import Q
    
    # Normalizar pergunta para comparação
    normalized_question = normalize_answer(question).strip()
    
    qs = Exercise.objects.filter(exercise_type=exercise_type)
    
    # Se usuário fornecido, filtrar por seu exercício
    if user:
        qs = qs.filter(created_by=user)
    
    # Buscar por pergunta similar (comparação normalizada)
    for ex in qs:
        if normalize_answer(ex.question).strip() == normalized_question:
            return True
    
    return False


def deduplicate_exercises(exercises, user=None):
    """
    Remove exercícios duplicados de uma lista.
    
    Detecta duplicatas por pergunta normalizada (case-insensitive, espaços).
    Mantém o primeiro, remove os posteriores.
    
    Args:
        exercises (list): Lista de Exercise objects (não salvos)
        user (User): Usuário proprietário (opcional)
    
    Returns:
        list: Lista de exercícios sem duplicatas internas e externas
    """
    from .models import Exercise
    
    seen_questions = set()
    deduplicated = []
    
    for ex in exercises:
        normalized_q = normalize_answer(ex.question).strip()
        
        # Skip se já visto nesta lista
        if normalized_q in seen_questions:
            continue
        
        # Skip se já existe no BD (para este usuário)
        if exercise_already_exists(ex.question, ex.exercise_type, user):
            continue
        
        seen_questions.add(normalized_q)
        deduplicated.append(ex)
    
    return deduplicated
