from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.postgres.fields import ArrayField

User = get_user_model()


# ---------- Языки ----------
LANGUAGES = [
    {'code': 'ru', 'name': 'Русский'},
    {'code': 'en', 'name': 'Английский'},
    {'code': 'fr', 'name': 'Французский'},
    {'code': 'es', 'name': 'Испанский'},
    {'code': 'cn', 'name': 'Китайский'},
]

class Language(models.Model):
    code = models.CharField(max_length=5, primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


# ---------- Общие справочники ----------
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class PartOfSpeech(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

class Author(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name


# ---------- Основная модель термина ----------
class Term(models.Model):
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    part_of_speech = models.ForeignKey(PartOfSpeech, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Term {self.id}"


class TermTranslation(models.Model):
    term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
        related_name='translations',
    )
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=100, null=True, blank=True)
    transliteration = models.CharField(max_length=255, null=True, blank=True)
    author = models.ForeignKey(Author, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = (('term', 'language'),)

    def __str__(self):
        return f"{self.name} ({self.language.code})"


class Definition(models.Model):
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='definitions')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    text = models.TextField()
    author = models.ForeignKey(Author, null=True, blank=True, on_delete=models.SET_NULL)
    embedding_json = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = (('term', 'language'),)

    def __str__(self):
        return f"Definition of Term {self.term.id} in {self.language.code}"


class Context(models.Model):
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='contexts')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    text = models.TextField()
    author = models.ForeignKey(Author, null=True, blank=True, on_delete=models.SET_NULL)
    embedding_json = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = (('term', 'language'),)

    def __str__(self):
        return f"Context of Term {self.term.id} in {self.language.code}"


# ---------- Специализированная модель DroneTerm ----------
class DroneTerm(models.Model):
    term_eng = models.CharField("Термин", max_length=100)
    abbr_eng = models.CharField("Термин на английском", max_length=100)
    category = models.CharField("Категория", max_length=100)
    part_references = models.CharField("Часть речи", max_length=100)
    term_rus = models.CharField("Термин на русском", max_length=100)
    abbr_rus = models.CharField("Аббревиатура на русском", max_length=100, blank=True, default='')
    definition_rus = models.TextField("Определение на русском")
    definition_eng = models.TextField("Определение на английском")
    context_eng = models.TextField("Контекст на английском")
    context_rus = models.TextField("Контекст на русском")
    embedding_json = models.TextField(null=True, blank=True)
    language = models.ForeignKey(
        Language,
        to_field='code',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.term_eng


# ---------- История поиска и избранное ----------
class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    term = models.ForeignKey(DroneTerm, on_delete=models.CASCADE)
    query = models.CharField(max_length=100)
    searched_at = models.DateTimeField(auto_now_add=True)


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    term = models.ForeignKey(DroneTerm, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'term')
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'

    def __str__(self):
        return f'{self.user.username} → {self.term.term_eng}'
