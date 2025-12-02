from typing import List, Optional
from .models import Vocabulary
from exercises.models import Exercise
import random
import os


def translate_text(text: str, target: str = 'en') -> Optional[str]:
    """Translate text using LibreTranslate public API as a simple free option.

    This is a best-effort helper. If the environment has an env var `LIBRETRANSLATE_URL`
    and `LIBRETRANSLATE_API_KEY`, it will use them; otherwise uses the public endpoint.
    Returns translated text or None on failure.
    """
    try:
        import requests
        from requests import RequestException
    except ImportError:
        return None
    
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
        return data.get('translatedText')
    except Exception:
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
