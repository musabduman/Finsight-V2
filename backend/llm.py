import os
import requests
from fastapi import APIRouter, HTTPException
from schemas import ChatRequest

router = APIRouter()
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")

SYSTEM_PROMPT = (
    "Sen FinSight adlı bir BIST hisse analiz asistanısın. Geleceği tahmin etmezsin; "
    "yalnızca geçmişte bir hissenin neden hareket ettiğini kısa, net ve Türkçe anlatırsın."
)


def ask_ollama(question: str) -> str:
    """Soruyu sistem promptuyla birlikte yerel Ollama modeline gönderir, cevap metnini döndürür."""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"{SYSTEM_PROMPT}\n\nKullanıcı sorusu: {question}",
        "stream": False,
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()["response"].strip()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Ollama'ya ulaşılamadı: {e}")


@router.post("/ask")
def ask(chat: ChatRequest):
    """Chatbot endpoint'i: soruyu alır, Ollama'dan üretilen cevabı döner."""
    return {"success": True, "answer": ask_ollama(chat.question)}