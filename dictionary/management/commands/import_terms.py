from django.core.management.base import BaseCommand
from dictionary.models import Term, TermTranslation, Definition, Context, Language, Category, PartOfSpeech
import psycopg2
from django.db import transaction
from dictionary.bert_model import embed_text
import json

class Command(BaseCommand):
    help = "Импорт терминов из таблицы raw_terms в полноценные модели Django"

    def handle(self, *args, **kwargs):
        conn = psycopg2.connect(
            dbname='bas_project',
            user='postgres',
            password='1337',
            host='localhost',
            port='5432'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM raw_terms")
        rows = cursor.fetchall()

        with transaction.atomic():
            for row in rows:
                term_eng, abbr_eng, category_name, pos_name, term_rus, abbr_rus, term_cn, pinyin, term_fr, abbr_fr, term_es, abbr_es, \
                def_rus, def_eng, def_fr, def_es, ctx_eng, ctx_rus, ctx_cn, ctx_fr, ctx_es = row

                category, _ = Category.objects.get_or_create(name=category_name or "Без категории")
                pos, _ = PartOfSpeech.objects.get_or_create(name=pos_name or "Не указана")
                term = Term.objects.create(category=category, part_of_speech=pos)

                # TermTranslations
                for lang_code, name, abbr, trans in [
                    ('en', term_eng, abbr_eng, None),
                    ('ru', term_rus, abbr_rus, None),
                    ('cn', term_cn, None, pinyin),
                    ('fr', term_fr, abbr_fr, None),
                    ('es', term_es, abbr_es, None),
                ]:
                    if name:
                        language = Language.objects.get(code=lang_code)
                        translation = TermTranslation.objects.create(
                            term=term,
                            language=language,
                            name=name.strip(),
                            abbreviation=abbr.strip() if abbr else None,
                            transliteration=trans.strip() if trans else None
                        )
                        # Добавим эмбеддинг для английского названия
                        if lang_code == 'en':
                            translation.term.embedding_json = json.dumps(embed_text(name.strip()))
                            translation.term.save()

                # Definitions
                for lang_code, definition in [('ru', def_rus), ('en', def_eng), ('fr', def_fr), ('es', def_es)]:
                    if definition:
                        language = Language.objects.get(code=lang_code)
                        def_obj = Definition.objects.create(
                            term=term,
                            language=language,
                            text=definition.strip()
                        )
                        def_obj.embedding_json = json.dumps(embed_text(definition.strip()))
                        def_obj.save()

                # Contexts
                for lang_code, context in [('ru', ctx_rus), ('en', ctx_eng), ('fr', ctx_fr), ('es', ctx_es), ('cn', ctx_cn)]:
                    if context:
                        language = Language.objects.get(code=lang_code)
                        ctx_obj = Context.objects.create(
                            term=term,
                            language=language,
                            text=context.strip()
                        )
                        ctx_obj.embedding_json = json.dumps(embed_text(context.strip()))
                        ctx_obj.save()

        self.stdout.write(self.style.SUCCESS("Импорт завершен успешно с эмбеддингами."))
