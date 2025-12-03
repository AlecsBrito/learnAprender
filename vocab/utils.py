from typing import List, Optional
from .models import Vocabulary
from exercises.models import Exercise
import random
import requests
from requests import RequestException
import os
import string


def translate_text(text: str, target: str = 'en') -> Optional[str]:
    """Translate text using multiple APIs with fallback.

    Tries LibreTranslate first, then falls back to other methods.
    Returns translated text or None on failure.
    """
    # Try LibreTranslate
    url = os.getenv('LIBRETRANSLATE_URL', 'https://libretranslate.de/translate')
    api_key = os.getenv('LIBRETRANSLATE_API_KEY')
    payload = {
        'q': text,
        'source': 'auto',
        'target': target,
        'format': 'text'
    }
    if api_key:
        payload['api_key'] = api_key
    try:
        r = requests.post(url, data=payload, timeout=6)
        r.raise_for_status()
        data = r.json()
        result = data.get('translatedText')
        if result:
            return result
    except Exception:
        pass
    
    # Fallback: Try mymemory translation API (free, no auth needed)
    try:
        url_fallback = f"https://api.mymemory.translated.net/get?q={text}&langpair=en|{target}"
        r = requests.get(url_fallback, timeout=5)
        r.raise_for_status()
        data = r.json()
        if data.get('responseStatus') == 200:
            result = data.get('responseData', {}).get('translatedText')
            if result and result != text:
                return result
    except Exception:
        pass
    
    return None


def fetch_dictionary_info(word: str) -> dict:
    """Try to fetch dictionary info (definitions, synonyms) from a public API.

    Returns a dict with keys 'definitions' and 'synonyms' when available.
    If network/API fails, returns empty dict.
    """
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        defs = []
        syns = []
        # Parse the typical response
        if isinstance(data, list):
            for entry in data:
                meanings = entry.get('meanings', [])
                for m in meanings:
                    for d in m.get('definitions', []):
                        text = d.get('definition')
                        if text:
                            defs.append(text)
                        s = d.get('synonyms') or []
                        for ss in s:
                            if ss:
                                syns.append(ss)
        return {'definitions': defs, 'synonyms': syns}
    except (RequestException, ValueError):
        return {}


def generate_exercises_for_vocab(vocab: Vocabulary, distractor_pool: List[Vocabulary] = None) -> List[Exercise]:
    """Generate a list of Exercise objects (not saved) based on a Vocabulary instance.

    Produces:
    - one 'translate' exercise (word -> translation)
    - one 'mcq' exercise with up to 3 distractors (translations)
    - optional 'gap' exercise if example contains the word
    """
    exercises = []

    # Try to enrich question with dictionary data
    info = fetch_dictionary_info(vocab.word)
    def_text = ''
    if info.get('definitions'):
        def_text = ' — ' + info['definitions'][0]

    # Try to back-translate or translate to gather better distractors
    back_translation = None
    translated_word = None
    try:
        translated_word = translate_text(vocab.word, target='en')
        if translated_word:
            back_translation = translate_text(translated_word, target='en')
    except Exception:
        translated_word = None
        back_translation = None

    # Translate exercise
    ex_trans = Exercise(
        question=f"Translate: {vocab.word}{def_text}",
        exercise_type='translate',
        answer=vocab.translation,
        level=vocab.level,
        category=vocab.category,
    )
    exercises.append(ex_trans)

    # MCQ exercise - build choices from distractor_pool if provided
    pool = distractor_pool or []
    # filter out same vocab
    pool_choices = [v for v in pool if v.pk != vocab.pk]
    random.shuffle(pool_choices)
    distractors = [p.translation for p in pool_choices[:3]]
    # If API provided synonyms, try to include them as distractor strings (best-effort)
    if info.get('synonyms'):
        for s in info['synonyms'][:3]:
            if s and s not in distractors and s != vocab.translation:
                distractors.append(s)

    # Use translation/back-translation to create additional plausible distractors
    if translated_word and translated_word not in distractors and translated_word != vocab.translation:
        distractors.append(translated_word)
    if back_translation and back_translation not in distractors and back_translation != vocab.translation:
        distractors.append(back_translation)
    mcq_choices = distractors + [vocab.translation]
    random.shuffle(mcq_choices)
    ex_mcq = Exercise(
        question=f"Which is the correct translation for: {vocab.word}?",
        exercise_type='mcq',
        choices=mcq_choices,
        answer=vocab.translation,
        level=vocab.level,
        category=vocab.category,
    )
    exercises.append(ex_mcq)

    # Gap fill: if example contains the word, replace it with a blank
    if vocab.example:
        example_lower = vocab.example.lower()
        word_lower = vocab.word.lower()
        if word_lower in example_lower:
            blanked = vocab.example.replace(vocab.word, '_____')
            ex_gap = Exercise(
                question=blanked,
                exercise_type='gap',
                answer=vocab.word,
                level=vocab.level,
                category=vocab.category,
            )
            exercises.append(ex_gap)

    return exercises


def get_random_words(count: int = 10) -> List[str]:
    """Fetch random English words from an API or database.
    
    Uses multiple word APIs with fallbacks. Returns list of random words (lowercase).
    """
    words = []
    
    # Try Random Word API first
    try:
        url = "https://random-word-api.herokuapp.com/all"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        all_words = resp.json()
        # Filter for reasonable length words (3-10 chars) and common ones
        filtered = [w for w in all_words if 3 <= len(w) <= 10 and w.isalpha() and not w.isupper()]
        if len(filtered) >= count:
            words = random.sample(filtered, count)
            return words
    except Exception:
        pass
    
    # If we couldn't get enough, use fallback common words list
    common_words = [
        'apple', 'book', 'coffee', 'dream', 'earth', 'forest', 'guitar', 'happy', 
        'island', 'journey', 'kitchen', 'lemon', 'mountain', 'novel', 'ocean', 'piano',
        'question', 'rainbow', 'summer', 'table', 'universe', 'village', 'window',
        'yellow', 'zebra', 'adventure', 'beautiful', 'camera', 'dangerous', 'elephant',
        'friend', 'generous', 'holiday', 'important', 'justice', 'knowledge', 'language',
        'medicine', 'nature', 'opinion', 'patience', 'quality', 'research', 'science',
        'technology', 'understand', 'valuable', 'weather', 'exercise', 'famous', 'grateful',
        'animal', 'bright', 'color', 'dollar', 'energy', 'family', 'garden', 'history',
        'leader', 'market', 'office', 'person', 'player', 'reason', 'school', 'server',
        'silver', 'soldier', 'supply', 'system', 'travel', 'village', 'visitor', 'winter',
    ]
    
    if words:
        # Combine with common words if we have some
        all_options = words + common_words
        return random.sample(all_options, min(count, len(all_options)))
    
    return random.sample(common_words, min(count, len(common_words)))


def fetch_word_definition_and_translation(word: str, target_lang: str = 'pt') -> tuple:
    """Fetch definition and translation for a word using public APIs.
    
    Returns tuple (definition, translation) or (None, None) if not found.
    """
    definition = None
    translation = None
    
    # Fetch definition from Dictionary API
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word.lower()}"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and len(data) > 0:
            meanings = data[0].get('meanings', [])
            if meanings:
                definitions = meanings[0].get('definitions', [])
                if definitions:
                    definition = definitions[0].get('definition')
    except Exception:
        pass
    
    # Fetch translation using LibreTranslate
    try:
        translation = translate_text(word, target=target_lang)
    except Exception:
        pass
    
    return definition, translation


def generate_exercises_from_random_words(count: int = 10, user_category: str = '') -> List[Exercise]:
    """Generate Exercise objects from random words fetched from external APIs.
    
    Each word generates:
    - One translation exercise
    - One MCQ exercise (if translation found)
    
    Returns list of unsaved Exercise objects.
    """
    exercises = []
    random_words = get_random_words(count)
    
    for word in random_words:
        try:
            definition, translation = fetch_word_definition_and_translation(word)
            
            # Skip if no translation found
            if not translation:
                continue
            
            # Translation exercise
            question_text = f"Translate: {word}"
            if definition:
                question_text += f" — {definition}"
            
            ex_trans = Exercise(
                question=question_text,
                exercise_type='translate',
                answer=translation,
                level='beginner',
                category=user_category or 'Random',
            )
            exercises.append(ex_trans)
            
            # Try to create MCQ exercise with random distractors
            try:
                # Get a few other words for distractors
                distractor_words = get_random_words(min(5, max(count - 2, 3)))
                distractor_translations = []
                
                for d_word in distractor_words:
                    if d_word.lower() == word.lower():
                        continue
                    _, d_trans = fetch_word_definition_and_translation(d_word)
                    if d_trans and d_trans != translation and d_trans.lower() != word.lower():
                        if len(distractor_translations) < 3:
                            distractor_translations.append(d_trans)
                
                # Only create MCQ if we have at least 2 distractors
                if len(distractor_translations) >= 2:
                    choices = distractor_translations + [translation]
                    random.shuffle(choices)
                    ex_mcq = Exercise(
                        question=f"Which is the correct translation for: {word}?",
                        exercise_type='mcq',
                        choices=choices,
                        answer=translation,
                        level='beginner',
                        category=user_category or 'Random',
                    )
                    exercises.append(ex_mcq)
            except Exception:
                # If MCQ generation fails, just skip it and continue
                pass
        
        except Exception:
            # Skip problematic words and continue with next
            continue
    
    return exercises
