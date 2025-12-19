from django.core.management.base import BaseCommand
from dictionary.models import DroneTerm
from sentence_transformers import SentenceTransformer
import json

class Command(BaseCommand):
    help = 'Генерирует эмбеддинги для всех терминов'

    def handle(self, *args, **kwargs):
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

        for term in DroneTerm.objects.all():
            text = f"{term.name or ''} {term.definition or ''}"
            embedding = model.encode(text).tolist()
            term.embedding_json = json.dumps(embedding)
            term.save()
            self.stdout.write(f"Эмбеддинг сгенерирован для: {term.name}")
