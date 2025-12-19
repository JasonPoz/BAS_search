from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import DroneTerm
from .serializers import DroneTermSerializer
from .bert_model import embed_text
from .utils import lemmatize_ru
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
import difflib

class DroneTermSearchAPI(APIView):
    def get(self, request):
        query = request.GET.get('q', '')
        if not query:
            return Response({"error": "Query param 'q' is required."}, status=status.HTTP_400_BAD_REQUEST)

        lemmatized = lemmatize_ru(query)
        query_vec = embed_text(lemmatized)
        results = []

        for term in DroneTerm.objects.exclude(embedding_json__isnull=True):
            try:
                term_vec = np.array(json.loads(term.embedding_json))
                similarity = cosine_similarity([query_vec], [term_vec])[0][0]
                if similarity > 0.5:
                    results.append((term, similarity))
            except Exception:
                continue

        # Fuzzy backup: fallback if no BERT match
        if not results:
            for term in DroneTerm.objects.all():
                if difflib.SequenceMatcher(None, query.lower(), term.term_eng.lower()).ratio() > 0.7:
                    results.append((term, 0.7))

        results.sort(key=lambda x: x[1], reverse=True)
        serialized = DroneTermSerializer([t[0] for t in results[:10]], many=True)
        return Response(serialized.data)
