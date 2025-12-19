from sentence_transformers import SentenceTransformer
import numpy as np

# Загружаем многоязычную модель
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def embed_text(text: str) -> list:
    """
    Преобразует текст в BERT-вектор (список чисел)
    """
    if not text:
        return []
    embedding = model.encode(text)
    return embedding.tolist()
