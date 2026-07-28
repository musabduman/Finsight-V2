import os
from ollama import Client
from fastapi import APIRouter, HTTPException
from backend.database.schema import ChatRequest
from backend.ai.embeddings import embed_query
from backend.database.db import search_similar_events

router = APIRouter()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.1")

SYSTEM_PROMPT = (
    "Sen FinSight adlı bir BIST hisse analiz asistanısın. "
    "Geleceği tahmin etmezsin. Sana verilen 'geçmiş örnekler' varsa "
    "cevabını onlara dayandırıp benzerlik kurarsın; yoksa dikkatli ve kısa "
    "bir genel yorum yaparsın. Her zaman net, anlaşılır Türkçe konuşursun. "
    "Yatırım tavsiyesi vermezsin, tarihsel örüntü paylaşırsın."
)


def _get_client() -> Client:
    """OLLAMA_API_KEY varsa Cloud, yoksa yerel Ollama bağlantısı açar."""
    kwargs: dict = {"host": OLLAMA_HOST}
    if OLLAMA_API_KEY:
        kwargs["headers"] = {"Authorization": f"Bearer {OLLAMA_API_KEY}"}
    return Client(**kwargs)


def build_context(events: list) -> str:
    """pgvector'dan dönen benzer geçmiş olayları LLM promptuna eklenecek metne çevirir."""
    if not events:
        return "Geçmiş veritabanında bu soruya yakın bir örnek bulunamadı."
    lines = []
    for e in events:
        etki = (
            f"sonraki günlerde %{e['price_change_pct']} değişim"
            if e["price_change_pct"] is not None
            else "fiyat etkisi bilinmiyor"
        )
        lines.append(
            f"- [{e['ticker']} | {e['published_at']}] {e['title']} "
            f"→ {etki} (benzerlik skoru: {e['similarity']:.2f})"
        )
    return "\n".join(lines)


def generate_answer(question: str, context: str) -> str:
    """Ollama'ya sistem promptu + kullanıcı sorusu + RAG bağlamı göndererek cevap üretir."""
    client = _get_client()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Soru: {question}\n\nGeçmiş Benzer Örnekler:\n{context}",
        },
    ]
    try:
        response = client.chat(
            model=LLM_MODEL,
            messages=messages,
            options={"temperature": 0.5, "num_predict": 400},
        )
        return response["message"]["content"].strip()
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"LLM servisi yanıt vermedi: {e}",
        )


@router.post("/ask")
def ask(chat: ChatRequest):
    """RAG akışı: soruyu embed et → pgvector'da benzer geçmiş olayları bul → Ollama cevap üret."""
    # 1. Embedding + vektör arama (DB yoksa graceful fallback)
    events = []
    try:
        query_vec = embed_query(chat.question)
        events = search_similar_events(query_vec, ticker=chat.ticker, k=3)
    except Exception as e:
        print(f"⚠️  RAG arama başarısız (DB/embedding sorun): {e}")

    # 2. Bağlamı string'e çevir
    context = build_context(events)

    # 3. LLM ile cevap üret
    answer = generate_answer(chat.question, context)

    # 4. events listesini JSON-serializable yap
    sources = [
        {
            "ticker": e["ticker"],
            "title": e["title"],
            "published_at": str(e["published_at"]),
            "similarity": round(float(e["similarity"]), 3),
            "price_change_pct": (
                round(float(e["price_change_pct"]), 2)
                if e["price_change_pct"] is not None
                else None
            ),
        }
        for e in events
    ]

    return {"success": True, "answer": answer, "sources": sources}
