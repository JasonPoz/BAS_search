# dictionary/utils.py

import spacy
import wikipedia

# Загружаем модель один раз при старте сервера
nlp_ru = spacy.load("ru_core_news_md")
wikipedia.set_lang("ru")


def lemmatize_ru(text):
    """Возвращает лемматизированный текст на русском."""
    return " ".join([token.lemma_ for token in nlp_ru(text)])

def get_wikipedia_summary(term):
    """Возвращает краткое описание термина из Википедии (если найден)."""
    try:
        return wikipedia.summary(term)
    except wikipedia.exceptions.PageError:
        return "Нет статьи в Википедии по этому термину."
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Слишком много значений: {e.options[:3]}"