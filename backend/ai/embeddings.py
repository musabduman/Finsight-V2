import os
import requests

OLLAMA_EMBED_URL = os.getenv("OLLAMA_EMBED_URL", "https://ollama.com")
EMBED_MODEL = os.getenv("EMBED_MODEL", "bge-m3")  # çok dilli, 1024 boyut — db.py'deki VECTOR(1024) ile uyumlu


def _embed(text: str) -> list:
    """Metni Ollama'nın embedding modeline gönderip vektörü döndürür."""
    response = requests.post(OLLAMA_EMBED_URL, json={"model": EMBED_MODEL, "input": text}, timeout=30)
    response.raise_for_status()
    return response.json()["embeddings"][0]


def embed_text(text: str) -> list:
    """Kaydedilecek haber metnini embed eder."""
    return _embed(text)


def embed_query(text: str) -> list:
    """Kullanıcı sorusunu embed eder (bge-m3 simetrik, e5'teki gibi ayrı prefix gerektirmiyor)."""
    return _embed(text)