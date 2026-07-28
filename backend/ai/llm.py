import os
import requests
from ollama import Client
from fastapi import APIRouter, HTTPException
from schemas import ChatRequest
from backend.ai.embeddings import embed_query
from backend.database.db import search_similar_events

router = APIRouter()

class BaseLLM:
    def build_prompt(self,*args,**kwargs):
        raise NotImplementedError

    def ask_ollama(self,prompt):
        raise NotImplementedError
    def __call__(self,*args,**kwargs):
        prompt=self.build_prompt(*args,**kwargs)
        return self.generate(prompt)


class OllamaChat(BaseLLM):
    def __init__(self, api_key=None, model="gpt-oss:120b-cloud"):
        self.model = model
        self.api_key = api_key or os.getenv("OLLAMA_API_KEY")
        if not self.api_key:
            raise ValueError("OLLAMA_API_KEY must be set in the environment or provided.")
        self.client = Client(
            host="https://ollama.com",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )

    def build_prompt(self, mesaj_gecmisi, aktif_baglam=""):
        
        # 🔥 HER MESAJDA YENİ HABER ÇEK (dinamik)
        """     
        dinamik_haber = get_memory_for_llm(
            query="BIST son haberler finans piyasa",
            limit=7
        )
        """

        system_content = f"""
            "Sen FinSight adlı bir BIST hisse analiz asistanısın. Geleceği tahmin etmezsin; "
            "sana verilen 'geçmiş örnekler' varsa cevabını onlara dayandırıp benzerlik kurarsın, "
            "yoksa dikkatli ve kısa bir genel yorum yaparsın. Her zaman net ve Türkçe konuşursun."
        """

        messages = [{"role": "system", "content": system_content}]
        messages.extend(mesaj_gecmisi)
        return messages

    def ask_ollama(self, chat_question, events):
        messages = self.build_prompt(chat_question, build_context(events))

        try:
            response = self.client.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": 0.5,
                    "num_predict": 400
                }
            )

            return response["message"]["content"].strip()

        except Exception as e:
            return f"⚠️ Chat error: {e}"
            
    @router.post("/ask")
    def ask(chat: ChatRequest):
        """RAG akışı: soruyu embed et → pgvector'da benzer geçmiş olayları bul → Ollama'dan cevap üret."""
        query_vec = embed_query(chat.question)
        events = search_similar_events(query_vec, ticker=chat.ticker, k=3)
        chatbot = OllamaChat()
        answer = chatbot.ask_ollama(chat.question, build_context(events))
        return {"success": True, "answer": answer, "sources": events}

def build_context(events: list) -> str:
    """pgvector'dan dönen benzer geçmiş olayları LLM promptuna eklenecek metne çevirir."""
    if not events:
        return "Geçmiş veritabanında bu soruya yakın bir örnek bulunamadı."
    satirlar = []
    for e in events:
        etki = f"sonraki günlerde %{e['price_change_pct']}" if e["price_change_pct"] is not None else "fiyat etkisi bilinmiyor"
        satirlar.append(f"- [{e['ticker']} | {e['published_at']}] {e['title']} → {etki} (benzerlik: {e['similarity']:.2f})")
    return "\n".join(satirlar)

