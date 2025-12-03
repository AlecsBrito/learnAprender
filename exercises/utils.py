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
