from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Prefetch
from difflib import get_close_matches
from deep_translator import GoogleTranslator
import json

from .models import (
    TermTranslation, Definition, Context, Language,
    SearchHistory, SearchQuery
)


class TermSearchView(ListView):
    """
    Поиск по исходному языку (source_lang) и вывод пары:
    source_lang -> target_lang (термин, определение, контекст).
    """
    model = TermTranslation
    template_name = 'pages/search_results.html'
    context_object_name = 'source_translations'

    source_lang_code = 'ru'
    target_lang_code = 'en'
    query_text = ''

    def get_queryset(self):
        # поддерживаем и ?q=, и ?query=
        self.query_text = (
            self.request.GET.get('q')
            or self.request.GET.get('query', '')
        ).strip()

        self.source_lang_code = (
            self.request.GET.get('source_lang')
            or self.request.GET.get('lang')
            or 'ru'
        ).strip()

        self.target_lang_code = (
            self.request.GET.get('target_lang')
            or 'en'
        ).strip()

        if not self.query_text:
            return TermTranslation.objects.none()

        translations = TermTranslation.objects.filter(
            language__code=self.source_lang_code
        )

        # 1) прямые совпадения
        direct = translations.filter(name__icontains=self.query_text)
        if direct.exists():
            return direct

        # 2) fuzzy / опечатки
        names = list(translations.values_list('name', flat=True))

        close_matches = get_close_matches(
            self.query_text,
            names,
            n=50,
            cutoff=0.5,
        )

        # fallback: пробуем без последнего символа
        if not close_matches and len(self.query_text) > 2:
            close_matches = get_close_matches(
                self.query_text[:-1],
                names,
                n=50,
                cutoff=0.5,
            )

        if not close_matches:
            return TermTranslation.objects.none()

        return translations.filter(name__in=close_matches)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        source_translations = context['source_translations']

        source_lang = Language.objects.filter(code=self.source_lang_code).first()
        target_lang = Language.objects.filter(code=self.target_lang_code).first()

        rows = []
        for src_tr in source_translations:
            term = src_tr.term

            tgt_tr = TermTranslation.objects.filter(
                term=term,
                language__code=self.target_lang_code
            ).first()

            def_src = Definition.objects.filter(
                term=term,
                language__code=self.source_lang_code
            ).first()
            def_tgt = Definition.objects.filter(
                term=term,
                language__code=self.target_lang_code
            ).first()

            ctx_src = Context.objects.filter(
                term=term,
                language__code=self.source_lang_code
            ).first()
            ctx_tgt = Context.objects.filter(
                term=term,
                language__code=self.target_lang_code
            ).first()

            rows.append({
                'src_term': src_tr,
                'tgt_term': tgt_tr,
                'src_def': def_src.text if def_src else '',
                'tgt_def': def_tgt.text if def_tgt else '',
                'src_ctx': ctx_src.text if ctx_src else '',
                'tgt_ctx': ctx_tgt.text if ctx_tgt else '',
            })

        extra_targets = Language.objects.exclude(
            code__in=[self.source_lang_code, self.target_lang_code]
        )

        # ✅ Сохраняем историю поиска (только если пользователь вошёл)
        if self.request.user.is_authenticated and self.query_text:
            # если хочешь — можно убрать SearchHistory совсем и оставить только SearchQuery,
            # но сейчас сохраняем в оба, чтобы ничего не потерять
            SearchHistory.objects.create(
                user=self.request.user,
                query=self.query_text
            )
            SearchQuery.objects.create(
                user=self.request.user,
                query=self.query_text,
                source_lang=self.source_lang_code,
                target_lang=self.target_lang_code,
                results_count=len(rows),
            )

        context.update({
            'rows': rows,
            'query': self.query_text,
            'source_lang': source_lang,
            'target_lang': target_lang,
            'extra_targets': extra_targets,
        })
        return context


class DictionaryView(ListView):
    model = TermTranslation
    template_name = 'pages/dictionary.html'
    context_object_name = 'translations'
    paginate_by = 30

    def get_queryset(self):
        lang_code = self.request.GET.get('lang', 'ru').strip()
        defs_qs = Definition.objects.filter(language__code=lang_code)

        return (
            TermTranslation.objects
            .filter(language__code=lang_code)
            .select_related('term', 'language')
            .prefetch_related(
                Prefetch('term__definitions', queryset=defs_qs, to_attr='defs_for_lang')
            )
            .order_by('name')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lang_code = self.request.GET.get('lang', 'ru').strip()

        context.update({
            'language': Language.objects.filter(code=lang_code).first(),
            'lang_code': lang_code,
            'languages': Language.objects.all().order_by('code'),
        })
        return context


def history_view(request):
    """
    Страница истории поиска пользователя.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    history = (
        SearchQuery.objects
        .filter(user=request.user)
        .order_by('-created_at')
    )

    return render(request, 'pages/history.html', {'history': history})


@require_GET
def autocomplete_terms(request):
    term = request.GET.get("term", "")
    results = list(
        TermTranslation.objects.filter(name__icontains=term)
        .values_list("name", flat=True)[:10]
    )
    return JsonResponse(results, safe=False)


@csrf_exempt
def translate_term(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    data = json.loads(request.body or '{}')
    term_id = data.get('term_id')
    target_lang = data.get('target_lang')

    if not term_id or not target_lang:
        return JsonResponse({'error': 'term_id and target_lang are required'}, status=400)

    try:
        src_translation = TermTranslation.objects.select_related('term', 'language').get(id=term_id)
    except TermTranslation.DoesNotExist:
        return JsonResponse({'error': 'Term not found'}, status=404)

    src_lang_code = src_translation.language.code

    target_translation = TermTranslation.objects.filter(
        term=src_translation.term,
        language__code=target_lang
    ).first()

    if target_translation:
        term_translated = target_translation.name
    else:
        try:
            term_translated = GoogleTranslator(source=src_lang_code, target=target_lang).translate(src_translation.name)
        except Exception:
            term_translated = ''

    def_src_obj = Definition.objects.filter(term=src_translation.term, language__code=src_lang_code).first()
    definition_source = def_src_obj.text if def_src_obj else ''

    def_tgt_obj = Definition.objects.filter(term=src_translation.term, language__code=target_lang).first()

    if def_tgt_obj:
        definition_translated = def_tgt_obj.text
    elif definition_source:
        try:
            definition_translated = GoogleTranslator(source=src_lang_code, target=target_lang).translate(definition_source)
        except Exception:
            definition_translated = ''
    else:
        definition_translated = ''

    ctx_src_obj = Context.objects.filter(term=src_translation.term, language__code=src_lang_code).first()
    context_source = ctx_src_obj.text if ctx_src_obj else ''

    ctx_tgt_obj = Context.objects.filter(term=src_translation.term, language__code=target_lang).first()

    if ctx_tgt_obj:
        context_translated = ctx_tgt_obj.text
    elif context_source:
        try:
            context_translated = GoogleTranslator(source=src_lang_code, target=target_lang).translate(context_source)
        except Exception:
            context_translated = ''
    else:
        context_translated = ''

    source_lang_name = (
        Language.objects.filter(code=src_lang_code)
        .values_list('name', flat=True)
        .first() or src_lang_code
    )
    target_lang_name = (
        Language.objects.filter(code=target_lang)
        .values_list('name', flat=True)
        .first() or target_lang
    )

    return JsonResponse({
        'term_source': src_translation.name,
        'term_translated': term_translated,
        'source_lang': src_lang_code,
        'source_lang_name': source_lang_name,
        'target_lang': target_lang,
        'target_lang_name': target_lang_name,
        'definition_source': definition_source,
        'definition_translated': definition_translated,
        'context_source': context_source,
        'context_translated': context_translated,
    })


def registration_view(request):
    return render(request, 'registration/registration-form.html')


def home(request):
    return render(request, 'pages/home.html')
